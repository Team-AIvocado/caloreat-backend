import pytest
from app.common.ai_utils import restore_original_inference


def test_restore_original_inference_mixed_case():
    """
    Case 1: LLM이 기존 답변(candidates) 중 하나를 선택하여 confidence를 높인 경우.
    Expectation: 1.1을 빼서 원래 점수로 복원해야 함.
    """
    # given
    enhanced_response = {
        "image_id": "test-uuid",
        "food_name": "Kimchi",
        "candidates": [
            {"label": "Kimchi", "confidence": 1.95},  # 0.85 + 1.1
            {"label": "Radish", "confidence": 0.4},
        ],
    }

    # when
    restored = restore_original_inference(enhanced_response)

    # then
    candidates = restored["candidates"]
    assert len(candidates) == 2
    assert candidates[0]["label"] == "Kimchi"
    assert candidates[0]["confidence"] == 0.85
    assert restored["food_name"] == "Kimchi"


def test_restore_original_inference_new_entry_case():
    """
    Case 2: LLM이 아예 새로운 답변을 생성하여 1순위로 넣은 경우.
    Expectation: 1순위(1.1)를 삭제하고, 2순위(원래 1순위)를 다시 Top 1으로 올려야 함.
    """
    # given
    enhanced_response = {
        "image_id": "test-uuid",
        "food_name": "Bibimbap",  # LLM이 새로 찾은 정답
        "candidates": [
            {"label": "Bibimbap", "confidence": 1.1},  # New from LLM
            {"label": "Fried Rice", "confidence": 0.7},  # Original Top 1
            {"label": "Salad", "confidence": 0.3},
        ],
    }

    # when
    restored = restore_original_inference(enhanced_response)

    # then
    candidates = restored["candidates"]
    assert len(candidates) == 2

    # 1.1 짜리는 삭제되어야 함
    assert "Bibimbap" not in [c["label"] for c in candidates]

    # 원래 1등이었던 Fried Rice가 다시 1등이 되어야 함
    assert candidates[0]["label"] == "Fried Rice"
    assert candidates[0]["confidence"] == 0.7

    # food_name도 복구되어야 함
    assert restored["food_name"] == "Fried Rice"


def test_restore_original_inference_no_candidates():
    """
    Case 3: 후보군이 없는 경우 (엣지 케이스)
    """
    # given
    response = {"image_id": "123", "candidates": []}

    # when
    restored = restore_original_inference(response)

    # then
    assert restored["candidates"] == []
    assert restored["food_name"] == ""
