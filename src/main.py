import re
import joblib

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
)
import torch

df = pd.read_csv("/home/lev0x/scratches/bertimbau/financial_messages.csv")

le = LabelEncoder()
df["label_id"] = le.fit_transform(df["label"])


def normalize_value(text):
    return re.sub(r"R\$ ?[\d\.,]+", "<VALOR>", text)


df["text"] = df["text"].apply(normalize_value)

train_texts, val_texts, train_labels, val_labels = train_test_split(
    df["text"].tolist(), df["label_id"].tolist(), test_size=0.2, random_state=42
)

model_name = "neuralmind/bert-base-portuguese-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=64)
val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=64)


class FinancialDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {key: torch.tensor(val[idx]) for key, val in self.encodings.items()} | {
            "labels": torch.tensor(self.labels[idx])
        }


train_dataset = FinancialDataset(train_encodings, train_labels)
val_dataset = FinancialDataset(val_encodings, val_labels)

num_labels = len(le.classes_)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name, num_labels=num_labels
)

training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=5,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
    eval_steps=100,
    save_strategy="steps",
    save_steps=100,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    eval_strategy="steps",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

trainer.train()
joblib.dump(le, "label_encoder.joblib")
