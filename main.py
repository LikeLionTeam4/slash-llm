"""
slash-llm — Gemma 추론 서비스

지금은 HTTP로 직접 받는다. 나중에 SQS에서 Job 받는 구조로 바꾼다.
"""

import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("LLM_MODEL", "gemma3:4b")
TIMEOUT = float(os.getenv("LLM_TIMEOUT", "120"))

# 입력 제한
# 짧은 글을 요약시키면 모델이 3줄을 채우려고 원문보다 길게 늘여 쓴다.
# 그런 입력은 애초에 요약 대상이 아니므로 여기서 막는다.
MIN_CHARS = int(os.getenv("SUMMARY_MIN_CHARS", "150"))
MAX_CHARS = int(os.getenv("SUMMARY_MAX_CHARS", "8000"))

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
    text = req.text.strip()

    if len(text) < MIN_CHARS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"요약할 만큼 긴 글이 아니다 ({len(text)}자, 최소 {MIN_CHARS}자). "
                "짧은 문장은 nlu에서 다른 명령으로 분류되어야 한다."
            ),
        )

    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]

    prompt = (
        "다음 글을 한국어로 요약해라.\n"
        "- 원문보다 짧게 쓴다\n"
        "- 최대 3문장\n"
        "- 요약문만 출력하고 다른 말은 붙이지 않는다\n"
        "- 원문에 없는 내용은 지어내지 않는다\n\n"
        f"{text}"
    )
    return SummaryResponse(summary=await ask_gemma(prompt), model=MODEL)
