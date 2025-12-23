from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.user_profile import UserProfileCrud
from app.db.crud.user_health_condition import HealthConditionCrud


# 상수 정의


# 활동 수준별 계수 (v0에서는 moderate 고정)
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,  # 거의 운동 안 함
    "light": 1.375,  # 가벼운 운동 (주 1-3회)
    "moderate": 1.55,  # 보통 운동 (주 3-5회) ← v0 기본값
    "active": 1.725,  # 활발한 운동 (주 6-7회)
    "very_active": 1.9,  # 매우 활발 (운동선수급)
}

# Goal별 칼로리 조정값
GOAL_CALORIE_ADJUSTMENTS = {
    "loss": -500,  # 감량: 하루 500kcal 적자
    "maintain": 0,  # 유지: 조정 없음
    "gain": 500,  # 증량: 하루 500kcal 잉여
}

# 권장 영양소 비율 (탄:단:지 = 50:25:25)
MACRO_RATIOS = {"carb": 0.50, "protein": 0.25, "fat": 0.25}

# 1g당 칼로리
CALORIES_PER_GRAM = {"carb": 4, "protein": 4, "fat": 9}

# 경고 기준값
WARNING_THRESHOLDS = {
    "diabetes_carb_ratio": 0.55,  # 당뇨: 탄수화물 55% 초과
    "hypertension_sodium_mg": 2000,  # 고혈압: 나트륨 2000mg 초과
    "hypotension_calorie_ratio": 0.70,  # 저혈압: 칼로리 70% 미만
    "hyperlipidemia_fat_g": 70,  # 고지혈증: 지방 70g 초과
}

# Goal별 칼로리 경고 기준
GOAL_WARNING_THRESHOLDS = {
    "loss": {"over": 1.10},  # 110% 초과 시 경고
    "maintain": {"under": 0.80, "over": 1.20},  # 80% 미만 또는 120% 초과
    "gain": {"under": 0.90},  # 90% 미만 시 경고
}


# 계산 함수


def calculate_age(birthdate: date) -> int:
    """생년월일로 나이 계산"""
    today = date.today()
    age = today.year - birthdate.year
    # 생일이 아직 안 지났으면 1살 빼기
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1
    return age


def calculate_bmr(gender: str, weight: float, height: float, age: int) -> float:
    """
    기초대사량(BMR) 계산 - Mifflin-St Jeor 공식

    Args:
        gender: "male" 또는 "female"
        weight: 체중 (kg)
        height: 키 (cm)
        age: 나이 (세)

    Returns:
        BMR (kcal)
    """
    if gender == "male":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:  # female
        return (10 * weight) + (6.25 * height) - (5 * age) - 161


def calculate_tdee(bmr: float, activity_level: str = "moderate") -> float:
    """
    일일 총 에너지 소비량(TDEE) 계산

    Args:
        bmr: 기초대사량
        activity_level: 활동 수준 (v0에서는 moderate 고정)

    Returns:
        TDEE (kcal)
    """
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return bmr * multiplier


def get_target_calorie(tdee: float, goal_type: str) -> float:
    """
    목표 칼로리 계산

    Args:
        tdee: 일일 총 에너지 소비량
        goal_type: "loss", "maintain", "gain"

    Returns:
        목표 칼로리 (kcal)
    """
    adjustment = GOAL_CALORIE_ADJUSTMENTS.get(goal_type, 0)
    return tdee + adjustment


def get_target_macros(target_calorie: float) -> dict:
    """
    목표 칼로리 기반 영양소별 목표량 계산

    Args:
        target_calorie: 목표 칼로리

    Returns:
        {"calorie": float, "carb": float, "protein": float, "fat": float}
    """
    return {
        "calorie": round(target_calorie, 1),
        "carb": round(
            (target_calorie * MACRO_RATIOS["carb"]) / CALORIES_PER_GRAM["carb"], 1
        ),
        "protein": round(
            (target_calorie * MACRO_RATIOS["protein"]) / CALORIES_PER_GRAM["protein"], 1
        ),
        "fat": round(
            (target_calorie * MACRO_RATIOS["fat"]) / CALORIES_PER_GRAM["fat"], 1
        ),
    }


# 경고 체크 함수


def check_goal_warnings(
    goal_type: str, total_calorie: float, target_calorie: float
) -> list[str]:
    """
    Goal(체중 목표) 기반 칼로리 경고 체크

    Args:
        goal_type: "loss", "maintain", "gain"
        total_calorie: 오늘 총 섭취 칼로리
        target_calorie: 목표 칼로리

    Returns:
        경고 코드 리스트
    """
    warnings = []

    if target_calorie <= 0:
        return warnings

    ratio = total_calorie / target_calorie
    thresholds = GOAL_WARNING_THRESHOLDS.get(goal_type, {})

    if "over" in thresholds and ratio > thresholds["over"]:
        warnings.append("GOAL_CALORIE_OVER")

    if "under" in thresholds and ratio < thresholds["under"]:
        warnings.append("GOAL_CALORIE_UNDER")

    return warnings


def check_condition_warnings(
    conditions: list[str],
    total_calorie: float,
    target_calorie: float,
    carb: float,
    fat: float,
    sodium: float,
) -> list[str]:
    """
    Health Condition(건강 상태) 기반 경고 체크

    Args:
        conditions: 건강 상태 리스트 ["diabetes", "hypertension", ...]
        total_calorie: 오늘 총 섭취 칼로리
        target_calorie: 목표 칼로리
        carb: 오늘 탄수화물 섭취량 (g)
        fat: 오늘 지방 섭취량 (g)
        sodium: 오늘 나트륨 섭취량 (mg)

    Returns:
        경고 코드 리스트
    """
    warnings = []

    # 당뇨 (diabetes): 탄수화물 비율 55% 초과
    if "diabetes" in conditions and total_calorie > 0:
        carb_ratio = (carb * CALORIES_PER_GRAM["carb"]) / total_calorie
        if carb_ratio > WARNING_THRESHOLDS["diabetes_carb_ratio"]:
            warnings.append("DIABETES_CARB_OVER")

    # 고혈압 (hypertension): 나트륨 2000mg 초과
    if "hypertension" in conditions:
        if sodium > WARNING_THRESHOLDS["hypertension_sodium_mg"]:
            warnings.append("HYPERTENSION_SODIUM_OVER")

    # 저혈압 (hypotension): 칼로리 70% 미만
    if "hypotension" in conditions and target_calorie > 0:
        if (
            total_calorie
            < target_calorie * WARNING_THRESHOLDS["hypotension_calorie_ratio"]
        ):
            warnings.append("HYPOTENSION_LOW_INTAKE")

    # 고지혈증 (hyperlipidemia): 지방 70g 초과
    if "hyperlipidemia" in conditions:
        if fat > WARNING_THRESHOLDS["hyperlipidemia_fat_g"]:
            warnings.append("HYPERLIPIDEMIA_FAT_OVER")

    return warnings


# 메인 서비스 클래스


class NutritionCalculatorService:
    """영양소 계산 및 조언 서비스"""

    @staticmethod
    async def get_user_target(db: AsyncSession, user_id: int) -> dict:
        """
        사용자의 목표 영양소 계산

        Returns:
            {"calorie": float, "carb": float, "protein": float, "fat": float}
        """
        # 사용자 프로필 조회
        profile = await UserProfileCrud.get_profile_db(db, user_id)

        if not profile:
            # 프로필 없으면 기본값 반환
            return get_target_macros(2000)

        # 나이 계산
        age = calculate_age(profile.birthdate) if profile.birthdate else 30

        # BMR 계산
        bmr = calculate_bmr(
            gender=profile.gender or "male",
            weight=profile.weight or 70,
            height=profile.height or 170,
            age=age,
        )

        # TDEE 계산 (v0: 활동량 moderate 고정)
        tdee = calculate_tdee(bmr, "moderate")

        # 목표 칼로리 계산
        target_calorie = get_target_calorie(tdee, profile.goal_type or "maintain")

        # 영양소별 목표량 계산
        return get_target_macros(target_calorie)

    @staticmethod
    async def get_warnings(
        db: AsyncSession,
        user_id: int,
        total_calorie: float,
        carb: float,
        protein: float,
        fat: float,
        sodium: float = 0,
    ) -> list[str]:
        """
        사용자 섭취량 기반 경고 생성

        Args:
            db: DB 세션
            user_id: 사용자 ID
            total_calorie: 오늘 총 칼로리
            carb: 오늘 탄수화물 (g)
            protein: 오늘 단백질 (g)
            fat: 오늘 지방 (g)
            sodium: 오늘 나트륨 (mg)

        Returns:
            경고 코드 리스트
        """
        warnings = []

        # 사용자 프로필 조회
        profile = await UserProfileCrud.get_profile_db(db, user_id)
        goal_type = profile.goal_type if profile else "maintain"

        # 목표 칼로리 계산
        target = await NutritionCalculatorService.get_user_target(db, user_id)
        target_calorie = target["calorie"]

        # Goal 기반 경고 체크
        goal_warnings = check_goal_warnings(goal_type, total_calorie, target_calorie)
        warnings.extend(goal_warnings)

        # Condition 조회 (문자열 리스트 반환)
        condition_list = await HealthConditionCrud.get_all_condition_db(db, user_id)
        condition_list = condition_list if condition_list else []

        # Condition 기반 경고 체크
        condition_warnings = check_condition_warnings(
            conditions=condition_list,
            total_calorie=total_calorie,
            target_calorie=target_calorie,
            carb=carb,
            fat=fat,
            sodium=sodium,
        )
        warnings.extend(condition_warnings)

        return warnings

    @staticmethod
    async def get_nutrition_advice(
        db: AsyncSession, user_id: int, current_intake: dict
    ) -> dict:
        """
        종합 영양 조언 반환 (메인 함수)

        Args:
            db: DB 세션
            user_id: 사용자 ID
            current_intake: 현재 섭취량
                {"calorie": float, "carb": float, "protein": float, "fat": float, "sodium": float}

        Returns:
            {
                "target": {"calorie": float, "carb": float, "protein": float, "fat": float},
                "current": {...},
                "warnings": [str, ...]
            }
        """
        # 목표 영양소 계산
        target = await NutritionCalculatorService.get_user_target(db, user_id)

        # 경고 생성
        warnings = await NutritionCalculatorService.get_warnings(
            db=db,
            user_id=user_id,
            total_calorie=current_intake.get("calorie", 0),
            carb=current_intake.get("carb", 0),
            protein=current_intake.get("protein", 0),
            fat=current_intake.get("fat", 0),
            sodium=current_intake.get("sodium", 0),
        )

        return {"target": target, "current": current_intake, "warnings": warnings}


# 영양소 기반 경고 (주간/월간용)


# 일일 권장량 기준 (성인 기준)
NUTRITION_THRESHOLDS = {
    # 과다 섭취 상한 (daily max)
    "sugar_max_g": 25,  # WHO 권장
    "sodium_max_mg": 2000,  # WHO 권장
    "cholesterol_max_mg": 300,  # FDA 권장
    "saturated_fat_max_g": 20,  # ~10% of 2000kcal
    "caffeine_max_mg": 400,  # FDA 권장
    # 부족 섭취 하한 (daily min)
    "fiber_min_g": 25,  # FDA 권장
    "vitamin_c_min_mg": 100,  # KDA 권장
    "calcium_min_mg": 1000,  # KDA 권장
}

# 경고 메시지 (프론트엔드 참조용)
NUTRITION_WARNING_MESSAGES = {
    # 과다 섭취
    "SUGAR_OVER": "당류 섭취가 권장량(25g)을 초과했습니다",
    "SODIUM_OVER": "나트륨 섭취가 권장량(2000mg)을 초과했습니다",
    "CHOLESTEROL_OVER": "콜레스테롤 섭취가 권장량(300mg)을 초과했습니다",
    "SATURATED_FAT_OVER": "포화지방 섭취가 권장량(20g)을 초과했습니다",
    "CAFFEINE_OVER": "카페인 섭취가 권장량(400mg)을 초과했습니다",
    # 부족 섭취
    "FIBER_UNDER": "식이섬유 섭취가 권장량(25g)에 부족합니다",
    "VITAMIN_C_UNDER": "비타민C 섭취가 권장량(100mg)에 부족합니다",
    "CALCIUM_UNDER": "칼슘 섭취가 권장량(1000mg)에 부족합니다",
}


def check_nutrition_warnings(daily_average: dict) -> list[str]:
    """
    일일 평균 섭취량 기반 영양소 경고 체크 (v1)

    Args:
        daily_average: 일일 평균 섭취량
            {
                "sugar": float,
                "fiber": float,
                "sodium": float,
                "cholesterol": float,
                "saturated_fat": float,
                "vitamin_c": float,
                "calcium": float,
                "caffeine": float,
            }

    Returns:
        경고 코드 리스트
    """
    warnings = []

    # 과다 섭취 체크
    if daily_average.get("sugar", 0) > NUTRITION_THRESHOLDS["sugar_max_g"]:
        warnings.append("SUGAR_OVER")

    if daily_average.get("sodium", 0) > NUTRITION_THRESHOLDS["sodium_max_mg"]:
        warnings.append("SODIUM_OVER")

    if daily_average.get("cholesterol", 0) > NUTRITION_THRESHOLDS["cholesterol_max_mg"]:
        warnings.append("CHOLESTEROL_OVER")

    if (
        daily_average.get("saturated_fat", 0)
        > NUTRITION_THRESHOLDS["saturated_fat_max_g"]
    ):
        warnings.append("SATURATED_FAT_OVER")

    if daily_average.get("caffeine", 0) > NUTRITION_THRESHOLDS["caffeine_max_mg"]:
        warnings.append("CAFFEINE_OVER")

    # 부족 섭취 체크
    if daily_average.get("fiber", 0) < NUTRITION_THRESHOLDS["fiber_min_g"]:
        warnings.append("FIBER_UNDER")

    if daily_average.get("vitamin_c", 0) < NUTRITION_THRESHOLDS["vitamin_c_min_mg"]:
        warnings.append("VITAMIN_C_UNDER")

    if daily_average.get("calcium", 0) < NUTRITION_THRESHOLDS["calcium_min_mg"]:
        warnings.append("CALCIUM_UNDER")

    return warnings
