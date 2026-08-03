"""
Gemma 요약 속도 측정.

서버를 먼저 켜고(uvicorn main:app) 다른 터미널에서 실행한다.

    python bench.py
"""

import statistics
import time

import httpx

URL = "http://localhost:8000/internal/v1/llm/summary"
RUNS = 3

SAMPLE = """
클라우드 컴퓨팅은 인터넷을 통해 서버, 스토리지, 데이터베이스, 네트워킹,
소프트웨어 등의 컴퓨팅 자원을 제공하는 방식이다. 사용자는 물리적인 장비를
직접 구매하고 관리할 필요 없이 필요한 만큼만 자원을 빌려 쓰고 사용한 만큼
비용을 지불한다. 이러한 방식은 초기 투자 비용을 크게 낮추고, 수요 변화에
빠르게 대응할 수 있게 해준다. 대표적인 서비스 모델로는 인프라를 제공하는
IaaS, 개발 플랫폼을 제공하는 PaaS, 완성된 소프트웨어를 제공하는 SaaS가 있다.
최근에는 서버 관리 자체를 신경 쓰지 않아도 되는 서버리스 방식과, 여러
클라우드를 함께 쓰는 멀티 클라우드 전략도 널리 쓰이고 있다.
""".strip()


def main() -> None:
    times = []

    for i in range(1, RUNS + 1):
        start = time.perf_counter()
        res = httpx.post(URL, json={"text": SAMPLE}, timeout=300)
        elapsed = time.perf_counter() - start
        res.raise_for_status()

        times.append(elapsed)
        print(f"[{i}/{RUNS}] {elapsed:.1f}초")
        if i == 1:
            print(f"      → {res.json()['summary'][:60]}...")

    print()
    print(f"평균 {statistics.mean(times):.1f}초 · 최소 {min(times):.1f}초 · 최대 {max(times):.1f}초")
    print()
    print("판단 기준")
    print("  5초 이하  → CPU로도 버틸 만함")
    print("  5~15초    → 애매함. 데모는 되지만 답답함")
    print("  15초 이상 → GPU 필요. 인프라 담당에게 전달")


if __name__ == "__main__":
    main()
