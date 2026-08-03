"""
slash-llm — Gemma 추론 서비스

지금은 HTTP로 직접 받는다. 나중에 SQS에서 Job 받는 구조로 바꾼다.
"""

import os

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("LLM_MODEL", "gemma3:4b")
TIMEOUT = float(os.getenv("LLM_TIMEOUT", "120"))

app = FastAPI(title="slash-llm")


class SummaryRequest(BaseModel):
    text: str


class SummaryResponse(BaseModel):
    summary: str
    model: str


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL}


async def ask_gemma(prompt: str) -> str:
    """Ollama에 물어보고 답만 꺼낸다."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": prompt, "stream": False},
        )
        res.raise_for_status()
        return res.json()["response"].strip()


@app.post("/internal/v1/llm/summary", response_model=SummaryResponse)
async def summary(req: SummaryRequest):
    prompt = (
        "다음 글을 한국어로 3줄 이내로 요약해라.\n"
        "요약문만 출력하고 다른 말은 붙이지 마라.\n\n"
        f"{req.text}"
    )
    return SummaryResponse(summary=await ask_gemma(prompt), model=MODEL)
