"""Transport와 무관한 요약 입력 정규화와 프롬프트 생성.

HTTP·Ollama에 의존하지 않아 실제 모델 없이 단위 시험이 가능하다. `main.py`가 이
모듈을 호출해 입력을 다듬은 뒤에만 Ollama로 보낸다.

두 가지를 한다.

``prepare_summary_text``
    공백을 제외한 글자 수가 최소치에 못 미치면 거부하고, 최대치를 넘으면 앞부분만
    남긴다. **모델에 보내기 전에 거른다** — 짧은 글을 요약시키면 모델이 분량을
    채우려고 원문보다 길게 늘여 쓰고, 긴 글은 컨텍스트를 넘겨 응답이 잘린다.

``build_summary_prompt``
    고정 시스템 지시와 원문을 조합한다. 대화 기억을 쓰지 않는 단건 생성이라 이전
    요청이 다음 요청에 영향을 주지 않는다.
"""


class SummaryInputTooShort(ValueError):
    def __init__(self, *, actual: int, minimum: int) -> None:
        self.actual = actual
        self.minimum = minimum
        super().__init__(f"요약할 만큼 긴 글이 아니다 ({actual}자, 최소 {minimum}자).")


def prepare_summary_text(text: str, *, minimum: int, maximum: int) -> str:
    normalized = text.strip()[:maximum]
    character_count = 0
    for character in normalized:
        if character.isspace():
            continue
        character_count += 1
        if character_count >= minimum:
            break
    if character_count < minimum:
        raise SummaryInputTooShort(actual=character_count, minimum=minimum)
    return normalized


def build_summary_prompt(text: str) -> str:
    return (
        "다음 글을 한국어로 요약해라.\n"
        "- 원문보다 짧게 쓴다\n"
        "- 최대 3문장\n"
        "- 요약문만 출력하고 다른 말은 붙이지 않는다\n"
        "- 원문에 없는 내용은 지어내지 않는다\n\n"
        f"{text}"
    )
