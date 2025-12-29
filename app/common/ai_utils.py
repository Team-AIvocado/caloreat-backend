import copy
from typing import Dict, Any


def restore_original_inference(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    LLM Fallback에 의해 수정된 응답(response)을 원본 AI 모델의 추론 결과로 복원
    MLOps 로깅을 위해 실제 모델의 성능(실패 포함)을 기록하기 위함입니다.

    Logic:
    1. confidence > 1.1 -> 기존 confidence에 1.1이 더해진 것이므로, 1.1을 뺍니다.
    2. confidence == 1.1 -> LLM에 의해 새로 생성된 항목이므로 삭제합니다.
    """
    # 원본 응답 변조 방지를 위해 깊은 복사
    restored = copy.deepcopy(response)

    candidates = restored.get("candidates", [])
    restored_candidates = []

    for cand in candidates:
        conf = cand.get("confidence", 0.0)

        # 1. 기존 항목이 LLM과 일치하여 점수가 뻥튀기된 경우 (원복)
        if conf > 1.1:
            cand["confidence"] = round(conf - 1.1, 4)  # 부동소수점 오차 방지
            restored_candidates.append(cand)

        # 2. LLM이 아예 새로운 정답을 가져온 경우 (삭제)
        elif conf == 1.1:
            continue

        # 3. 그 외 (점수 낮은 기존 항목들)
        else:
            restored_candidates.append(cand)

    # 리스트 교체
    restored["candidates"] = restored_candidates

    # food_name 재설정 (Top 1이 바뀌었을 수 있음)
    if restored_candidates:
        # confidence 기준으로 다시 정렬 (혹시 순서가 섞였을 경우 대비)
        restored_candidates.sort(key=lambda x: x["confidence"], reverse=True)
        restored["food_name"] = restored_candidates[0]["label"]
    else:
        # 매우 희소하지만 원본 후보가 하나도 없었던 경우? (혹은 LLM 결과만 있었던 경우)
        # 빈 상태로 둡니다.
        restored["food_name"] = ""

    return restored
