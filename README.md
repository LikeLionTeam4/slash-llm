# Slash | LLM 서비스

Slash(/)는 자연어 질문과 `/` 슬래시 명령어를 한 입력창에서 처리하는 AI 에이전트 서비스입니다.
이 저장소는 그중 **LLM 추론** 파트를 담당합니다.

## 역할

- Gemma 모델 실행
- 요약 생성

현재 MVP는 `TEXT_SUMMARY`만 제공한다. 일반 대화와 SQS worker는 구현 범위가 아니다.

## 시작하기

### 1. Ollama 준비

```bash
# https://ollama.com 에서 설치 후
ollama pull gemma3:4b
```

### 2. 실행

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. 확인

브라우저에서 http://localhost:8000/docs

### 환경변수

| 이름 | 기본값 | 설명 |
|---|---|---|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama 주소 |
| `LLM_MODEL` | `gemma3:4b` | 사용할 모델 |
| `LLM_TIMEOUT` | `120` | 응답 대기 시간(초) |
| `SUMMARY_MIN_CHARS` | `150` | 요약 요청 최소 글자 수 |
| `SUMMARY_MAX_CHARS` | `8000` | 모델에 전달할 최대 글자 수 |
| `LLM_MAX_CONCURRENT_REQUESTS` | `1` | 프로세스당 동시 모델 호출 수 |
| `LLM_BUSY_RETRY_AFTER` | `1` | 과부하 응답의 재시도 권고 시간(초) |

### API

| 메서드 | 경로 | 설명 |
|---|---|---|
| `GET` | `/health` | 상태 확인 |
| `POST` | `/internal/v1/llm/summary` | 텍스트 요약 |

```bash
curl -X POST http://localhost:8000/internal/v1/llm/summary \
  -H "Content-Type: application/json" \
  -d '{"text": "요약할 긴 글"}'
```

기존 요청과 응답은 그대로 사용할 수 있다.

```json
{
  "text": "150자 이상의 요약할 원문"
}
```

```json
{
  "summary": "생성된 요약",
  "model": "gemma3:4b"
}
```

요청 추적이 필요하면 `requestId`, `taskId`를 선택적으로 전달한다. 제공한 값만
성공 또는 오류 응답에 그대로 포함된다.

```json
{
  "text": "150자 이상의 요약할 원문",
  "requestId": "request-1",
  "taskId": "task-1"
}
```

150자 미만은 `400`으로 거부하고, 8000자 초과 입력은 기존 동작과 같이 앞의
8000자만 모델에 전달한다.

### 오류 응답

```json
{
  "error": {
    "code": "MODEL_TIMEOUT",
    "message": "모델 응답 시간이 초과되었다.",
    "retryable": true
  },
  "requestId": "request-1",
  "taskId": "task-1"
}
```

| HTTP | 코드 | 재시도 | 조건 |
|---:|---|---:|---|
| 400 | `INPUT_TOO_SHORT` | 아니요 | 공백 제거 후 150자 미만 |
| 503 | `MODEL_UNAVAILABLE` | 예 | Ollama 연결 실패 |
| 503 | `MODEL_BUSY` | 예 | 동시 모델 호출 한도 초과; `Retry-After` 포함 |
| 504 | `MODEL_TIMEOUT` | 예 | Ollama timeout |
| 502 | `UPSTREAM_ERROR` | 예 | Ollama 4xx/5xx 응답 |
| 502 | `INVALID_MODEL_RESPONSE` | 예 | 비 JSON, 필드 누락, 빈 결과 |

Pydantic 요청 형식 검증 실패는 FastAPI 기본 `422` 응답을 사용한다.

사용자/IP별 요청 횟수 제한은 인증 정보를 가진 `slash-api`가 담당합니다. 권장
계약은 HTTP `429`, 오류 코드 `RATE_LIMITED`, `Retry-After` 헤더입니다. 이
서비스의 `MODEL_BUSY`는 사용자 제한이 아니라 Ollama 자원 보호용입니다.

## 테스트

자동 테스트는 실제 Ollama를 호출하지 않는다.

```bash
pytest
python -m compileall .
```

실제 모델을 포함한 로컬 수동 시험은 서버와 Ollama를 실행한 뒤 진행한다.

```bash
python samples.py
python bench.py
```

## 관련 저장소

| 저장소 | 역할 |
|---|---|
| [slash-web](https://github.com/LikeLionTeam4/slash-web) | 웹 클라이언트 — React·Vite UI, S3/CloudFront 배포 |
| [slash-api](https://github.com/LikeLionTeam4/slash-api) | 코어 API — 인증, 작업 관리, 실행 위치 결정, DB 연동 |
| [slash-nlu](https://github.com/LikeLionTeam4/slash-nlu) | 자연어 분석 — slash 명령 파싱, 규칙·Kiwi 의도 분류, 인자 추출 |
| **slash-llm** (현재) | LLM 서비스 — Gemma 추론, 요약·대화 생성 |
| [slash-agent](https://github.com/LikeLionTeam4/slash-agent) | 로컬 에이전트 — PC 파일 검색, 상태 조회, 로컬 AI 실행·결과 전달 |
| [slash-infra](https://github.com/LikeLionTeam4/slash-infra) | 인프라 — Terraform(AWS), Helm·ArgoCD 배포 |
| [slash-docs](https://github.com/LikeLionTeam4/slash-docs) | 프로젝트 문서 — 아키텍처, API 계약, ERD, 회의록 |
