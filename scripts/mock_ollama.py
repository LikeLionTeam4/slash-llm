"""Small Ollama-compatible server used by the teammate smoke test."""

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="slash mock Ollama")


class GenerateRequest(BaseModel):
    model: str
    prompt: str
    stream: bool = False


@app.get("/api/tags")
def tags():
    return {"models": [{"name": "team-demo"}]}


@app.post("/api/generate")
def generate(request: GenerateRequest):
    del request
    return {"response": "팀 테스트용 요약 결과입니다."}
