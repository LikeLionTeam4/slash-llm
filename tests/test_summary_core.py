import pytest

from summary_core import SummaryInputTooShort, build_summary_prompt, prepare_summary_text


def test_prepare_summary_text_strips_and_truncates():
    assert prepare_summary_text("  " + ("가" * 151) + "  ", minimum=150, maximum=150) == "가" * 150


def test_prepare_summary_text_rejects_short_input():
    with pytest.raises(SummaryInputTooShort) as exc_info:
        prepare_summary_text("가" * 149, minimum=150, maximum=8000)

    assert exc_info.value.actual == 149
    assert exc_info.value.minimum == 150


def test_prompt_core_has_no_transport_fields():
    prompt = build_summary_prompt("원문")

    assert prompt.endswith("원문")
    assert "requestId" not in prompt
    assert "taskId" not in prompt
