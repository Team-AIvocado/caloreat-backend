from fastapi import APIRouter

# Users
from . import user
from . import user_profile
from . import user_health_condition
from . import user_profile_form

# Meals
from . import meal

# Stats
from . import stats

# ai
from . import ai_feedback
from . import logs


# from . import user_allergy

router = APIRouter()

# fastapi 팀 권장 패턴(정적 include) ∵ 안전성 + 가독성

# Users
router.include_router(user.router)
router.include_router(user_profile.router)
router.include_router(user_health_condition.router)
router.include_router(user_profile_form.router)
# Meals
router.include_router(meal.router)
# Stats
router.include_router(stats.stats_router)
router.include_router(stats.dashboard_router)
# AI
router.include_router(ai_feedback.router)
# Admin
router.include_router(logs.router)


# 변경: 도메인만모아서 한 객체로 반환
__all__ = ["router"]


# router.include_router(user_allergy.router) #deleted


# 추가 고려 가능
# import importlib
# import pkgutil

# # 3. gpt - 동적 자동스캔방식
# for _, module_name, _ in pkgutil.iter_modules(__path__):
#     module = importlib.import_module(f"{__name__}.{module_name}")
#     if hasattr(module, "router"):
#         router.include_router(module.router)
