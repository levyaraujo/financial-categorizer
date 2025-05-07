from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from src.inference import predict_category, load_model_and_tokenizer
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_time = time.time()
    logger.info("Starting model and tokenizer loading...")
    model, tokenizer = load_model_and_tokenizer()
    app.state.model = model
    app.state.tokenizer = tokenizer
    logger.info(f"Model and tokenizer loaded in {time.time() - start_time:.2f} seconds")
    yield


app = FastAPI(lifespan=lifespan)


class Message(BaseModel):
    message: str


@app.post("/categorize")
async def categorize(message: Message):
    start_time = time.time()
    logger.info(f"Received request for message: {message.message[:50]}...")

    model = app.state.model
    tokenizer = app.state.tokenizer

    inference_start = time.time()
    category = predict_category(message.message, model, tokenizer)
    inference_time = time.time() - inference_start
    logger.info(f"Inference completed in {inference_time:.2f} seconds")

    total_time = time.time() - start_time
    logger.info(f"Total request processing time: {total_time:.2f} seconds")

    return {"category": category, "processing_time_ms": round(total_time * 1000, 2)}
