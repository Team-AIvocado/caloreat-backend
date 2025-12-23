from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta, datetime
from typing import List, Dict
from app.db.crud.meal_log import MealLogCrud
from app.services.user_profile import UserProfileService
from app.db.schemas.stats import (
    StatsResponse,
    Nutrients,
    NutrientDetail,
    ChartData,
    DailyLogItem,
    Goals,
)

class StatsService:
    @staticmethod
    def get_nutrient_goals(goal_calories: float) -> Goals:
        """
        목표 칼로리를 기반으로 영양소별 권장 섭취량 계산
        """
        return Goals(
            sugar=round((goal_calories * 0.1) / 4, 1),  # 10% of calories, 4kcal/g
            fiber=round((goal_calories / 1000) * 14, 1),  # 14g per 1000kcal
            sodium=2000.0,  # 2000mg (standard limit)
            cholesterol=300.0,  # 300mg (standard limit)
            saturated_fat=round((goal_calories * 0.1) / 9, 1)  # 10% of calories, 9kcal/g
        )

    @staticmethod
    async def calculate_goal_calories(db: AsyncSession, user_id: int) -> float:
        """
        유저의 BMR을 기반으로 목표 칼로리 계산
        """
        try:
            # 유저 프로필 정보(키, 몸무게, 나이, 성별) 조회
            profile = await UserProfileService.get_profile(db, user_id)
            if not profile:
                return 2400.0
            
            # BMR 계산
            if profile.gender == "male":
                bmr = 66.47 + (13.75 * profile.weight) + (5 * profile.height) - (6.76 * profile.age)
            else:
                bmr = 655.1 + (9.56 * profile.weight) + (1.85 * profile.height) - (4.68 * profile.age)
            
            return round(bmr)
        except Exception:
            # 프로필 정보가 없거나 에러 발생 시 기본값 반환
            return 2400.0

    @staticmethod
    def aggregate_nutrients(meal_logs, divisor: int = 1) -> Nutrients:
        """
        식단 로그들로부터 영양소 합계 계산 및 평균화
        """
        total_carbs = 0.0
        total_protein = 0.0
        total_fat = 0.0
        total_sugar = 0.0
        total_fiber = 0.0
        total_sodium = 0.0
        total_cholesterol = 0.0
        total_saturated_fat = 0.0

        # 모든 식단 로그와 그 안의 음식 항목들을 순회하며 영양소 합산
        for log in meal_logs:
            for item in log.meal_items:
                nutritions = item.nutritions or {}
                quantity = item.quantity or 1.0
                # intake(quantity) 값을 반영하여 합산
                total_carbs += nutritions.get("carbs_g", 0) * quantity
                total_protein += nutritions.get("protein_g", 0) * quantity
                total_fat +=nutritions.get("fat_g", 0) * quantity
                total_sugar += nutritions.get("sugar_g", 0) * quantity
                total_fiber +=  nutritions.get("fiber_g", 0) * quantity
                total_sodium += nutritions.get("sodium_mg", 0) * quantity
                total_cholesterol += nutritions.get("cholesterol_mg", 0) * quantity
                total_saturated_fat +=nutritions.get("saturated_fat_g", 0) * quantity

        # 탄단지 비율 계산
        total_macro = total_carbs + total_protein + total_fat
        if total_macro > 0:
            carbs_pct = (total_carbs / total_macro) * 100
            protein_pct = (total_protein / total_macro) * 100
            fat_pct = (total_fat / total_macro) * 100
        else:
            carbs_pct = protein_pct = fat_pct = 0.0

        # divisor(일수)로 나누어 평균값 계산 후 반환
        return Nutrients(
            carbs=NutrientDetail(amount=round(total_carbs / divisor, 1), percentage=round(carbs_pct, 1)),
            protein=NutrientDetail(amount=round(total_protein / divisor, 1), percentage=round(protein_pct, 1)),
            fat=NutrientDetail(amount=round(total_fat / divisor, 1), percentage=round(fat_pct, 1)),
            sugar=round(total_sugar / divisor, 1),
            fiber=round(total_fiber / divisor, 1),
            sodium=round(total_sodium / divisor, 1),
            cholesterol=round(total_cholesterol / divisor, 1),
            saturated_fat=round(total_saturated_fat / divisor, 1)
        )

    @staticmethod
    async def get_daily_stats(db: AsyncSession, user_id: int, target_date: date) -> StatsResponse:
        """
        일간 통계 조회
        """
        # 해당 날짜의 모든 식단 로그 조회
        meal_logs = await MealLogCrud.get_meal_logs_db(db, user_id, target_date)
        goal_calories = await StatsService.calculate_goal_calories(db, user_id)
        nutrient_goals = StatsService.get_nutrient_goals(goal_calories)
        
        # 영양소 합계 계산
        nutrients = StatsService.aggregate_nutrients(meal_logs, divisor=1)
        total_calories = sum(
            sum(item.nutritions.get("calories", 0) * (item.quantity or 1.0) for item in log.meal_items if item.nutritions)
            for log in meal_logs
        )

        # 프론트엔드 표시용 개별 식단 로그 리스트 생성
        daily_logs = []
        for log in meal_logs:
            log_calories = sum(item.nutritions.get("calories", 0) * (item.quantity or 1.0) for item in log.meal_items if item.nutritions)
            name = ", ".join([item.foodname for item in log.meal_items])
            daily_logs.append(DailyLogItem(
                id=log.id,
                mealType=log.meal_type,
                timestamp=log.eaten_at.strftime("%H:%M"),
                name=name,
                calories=round(log_calories, 1)
            ))

        return StatsResponse(
            type="daily",
            date=str(target_date),
            totalCalories=round(total_calories, 1),
            nutrients=nutrients,
            goals=nutrient_goals,
            dailyLogs=daily_logs,
            showAlert=total_calories > 0  # 칼로리가 0이면 알림 미표시
        )

    @staticmethod
    async def get_weekly_stats(db: AsyncSession, user_id: int, end_date: date) -> StatsResponse:
        """
        주간 통계 조회 (end_date 포함 이전 7일)
        """
        # 7일간의 시작 날짜 계산
        start_date = end_date - timedelta(days=6)
        # 기간 내 모든 식단 로그 조회
        meal_logs = await MealLogCrud.get_meal_logs_by_range_db(db, user_id, start_date, end_date)
        goal_calories = await StatsService.calculate_goal_calories(db, user_id)
        nutrient_goals = StatsService.get_nutrient_goals(goal_calories)
        
        # 어플 시작일 고려하여 평균 계산을 위한 divisor 결정
        first_log_date = await MealLogCrud.get_first_meal_log_date_db(db, user_id)
        if first_log_date:
            # (종료일 - 시작일 + 1)과 (종료일 - 첫 기록일 + 1) 중 작은 값 사용
            days_since_start = (end_date - first_log_date).days + 1
            divisor = max(1, min(7, days_since_start))
        else:
            divisor = 7

        # 평균 영양소 계산
        nutrients = StatsService.aggregate_nutrients(meal_logs, divisor=divisor)
        total_calories = sum(
            sum(item.nutritions.get("calories", 0) * (item.quantity or 1.0) for item in log.meal_items if item.nutritions)
            for log in meal_logs
        )

        # 차트 데이터 생성 (7일치 일별 칼로리)
        chart_data = []
        logs_by_date = {}
        for log in meal_logs:
            d = log.eaten_at.date()
            logs_by_date[d] = logs_by_date.get(d, 0) + sum(item.nutritions.get("calories", 0) * (item.quantity or 1.0) for item in log.meal_items if item.nutritions)

        for i in range(7):
            current = start_date + timedelta(days=i)
            chart_data.append(ChartData(
                name=f"{current.month}/{current.day}",
                calories=round(logs_by_date.get(current, 0), 1),
                goal=goal_calories
            ))

        return StatsResponse(
            type="weekly",
            date=str(end_date),
            totalCalories=round(total_calories / divisor, 1),
            nutrients=nutrients,
            goals=nutrient_goals,
            chartData=chart_data,
            showAlert=total_calories > 0  # 칼로리가 0이면 알림 미표시
        )

    @staticmethod
    async def get_monthly_stats(db: AsyncSession, user_id: int, year: int, month: int) -> StatsResponse:
        """
        월간 통계 조회
        """
        import calendar
        # 해당 월의 마지막 날짜 계산
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        
        # 월간 모든 식단 로그 조회
        meal_logs = await MealLogCrud.get_meal_logs_by_range_db(db, user_id, start_date, end_date)
        goal_calories = await StatsService.calculate_goal_calories(db, user_id)
        nutrient_goals = StatsService.get_nutrient_goals(goal_calories)
        
        # 어플 시작일 고려하여 평균 계산을 위한 divisor 결정
        first_log_date = await MealLogCrud.get_first_meal_log_date_db(db, user_id)
        if first_log_date:
            # (해당 월의 일수)와 (종료일 - 첫 기록일 + 1) 중 작은 값 사용
            days_since_start = (end_date - first_log_date).days + 1
            divisor = max(1, min(last_day, days_since_start))
        else:
            divisor = last_day

        # 월 평균 영양소 계산
        nutrients = StatsService.aggregate_nutrients(meal_logs, divisor=divisor)
        total_calories = sum(
            sum(item.nutritions.get("calories", 0) * (item.quantity or 1.0) for item in log.meal_items if item.nutritions)
            for log in meal_logs
        )

        # 차트 데이터 생성 (주차별 평균 칼로리)
        chart_data = []
        weeks = [0.0, 0.0, 0.0, 0.0]
        for log in meal_logs:
            day = log.eaten_at.day
            calories = sum(item.nutritions.get("calories", 0) * (item.quantity or 1.0) for item in log.meal_items if item.nutritions)
            if day <= 7: weeks[0] += calories
            elif day <= 14: weeks[1] += calories
            elif day <= 21: weeks[2] += calories
            else: weeks[3] += calories

        today = date.today()
        for i, val in enumerate(weeks):
            # 해당 주의 마지막 날짜 계산
            week_end_day = (i + 1) * 7
            if i == 3: week_end_day = last_day
            
            try:
                week_end_date = date(year, month, week_end_day)
            except ValueError:
                # 월말 날짜가 7의 배수가 아닐 경우 처리
                week_end_date = date(year, month, last_day)

            # 미래의 주 평균 값은 출력되지 않게 처리
            if week_end_date > today:
                continue

            chart_data.append(ChartData(
                name=f"{i+1}주",
                calories=round(val / 7, 1),
                goal=goal_calories
            ))

        return StatsResponse(
            type="monthly",
            date=f"{year}-{month:02d}",
            totalCalories=round(total_calories / divisor, 1),
            nutrients=nutrients,
            goals=nutrient_goals,
            chartData=chart_data,
            showAlert=total_calories > 0  # 칼로리가 0이면 알림 미표시
        )
