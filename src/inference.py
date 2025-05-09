import os
import re
import time
import logging
import functools

import joblib
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F
import torch.nn as nn
import dotenv

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

le = joblib.load("label_encoder.joblib")
MODEL_PATH = os.getenv("MODEL_PATH")


def normalize_value(text):
    return re.sub(r"R\$ ?[\d\.,]+|[\d\.,]+", "<VALOR>", text)


@functools.lru_cache(maxsize=1)
def load_model_and_tokenizer(
    model_path=MODEL_PATH,
):
    start_time = time.time()
    logger.info("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("neuralmind/bert-base-portuguese-cased")
    logger.info(f"Tokenizer loaded in {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    logger.info("Loading model...")
    model = AutoModelForSequenceClassification.from_pretrained(model_path)

    # Quantize the model to int8
    logger.info("Quantizing model...")
    model = torch.quantization.quantize_dynamic(model, {nn.Linear}, dtype=torch.qint8)

    # Convert model to TorchScript for better CPU performance
    logger.info("Optimizing with TorchScript...")
    model.eval()

    # Optimize memory usage
    torch.cuda.empty_cache()

    logger.info(f"Model loaded and optimized in {time.time() - start_time:.2f} seconds")
    return model, tokenizer


def predict_category(message: str, model, tokenizer):
    start_time = time.time()
    message = normalize_value(message)

    tokenize_start = time.time()
    inputs = tokenizer(
        message, return_tensors="pt", truncation=True, padding=True, max_length=64
    )
    logger.info(f"Tokenization completed in {time.time() - tokenize_start:.2f} seconds")

    inference_start = time.time()
    with torch.no_grad():
        with torch.inference_mode():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = F.softmax(logits, dim=1)
            predicted_class = torch.argmax(probs, dim=1).item()

    logger.info(
        f"Model inference completed in {time.time() - inference_start:.2f} seconds"
    )

    category = le.inverse_transform([predicted_class])[0]
    logger.info(f"Total prediction time: {time.time() - start_time:.2f} seconds")
    return category


if __name__ == "__main__":
    while True:
        model, tokenizer = load_model_and_tokenizer()

        msg = str(input("Mensagem: "))

        print("=" * 80)
        print(f"Mensagem: {normalize_value(msg)}")
        print(f"Categoria: {predict_category(msg, model, tokenizer)}")
