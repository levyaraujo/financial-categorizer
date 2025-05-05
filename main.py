from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from src.inference import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    model, tokenizer = load_model_and_tokenizer()
    app.state.model = model
    app.state.tokenizer = tokenizer
    app.state.model.eval()
    yield


app = FastAPI(lifespan=lifespan)


class Message(BaseModel):
    message: str


@app.post("/categorize")
async def categorize(message: Message):
    model = app.state.model
    tokenizer = app.state.tokenizer

    category = predict_category(message.message, model, tokenizer)
    return {"category": category}