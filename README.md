# Slash | LLM 서비스

Slash(/)는 자연어 질문과 `/` 슬래시 명령어를 한 입력창에서 처리하는 AI 에이전트 서비스입니다.
이 저장소는 그중 **LLM 추론** 파트를 담당합니다.

## 역할

- Gemma 모델 실행
- 요약 생성
- 대화 생성

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

> 지금은 HTTP로 직접 받습니다. 이후 SQS에서 Job을 받아 처리하고
> 결과를 slash-api로 돌려주는 워커 구조로 바꿉니다.

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
