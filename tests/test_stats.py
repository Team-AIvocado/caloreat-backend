import pytest
from datetime import date

# --- Stats Router Tests ---


# TODO: 스키마 확정되면 주석 참고해서 200 응답 테스트 추가하기


def test_today_summary_unauthorized(client):
    response = client.get("/api/v1/dashboard/today")
    assert response.status_code == 401


# def test_today_summary_authorized(authorized_client):
#     # Depending on implementation "pass", it might return null or 500 if not handled,
#     # but since it returns "pass" implicitly returns None (200 OK with null body or validation error if schema doesn't allow null).
#     # The schema TodaySummary is defined. If it returns None and validation fails, we might see 500 or 422.
#     # But current implementation in stats.py is just `pass`, so it returns `null` JSON.
#     # We just want to check Auth passed (so not 401).
#     response = authorized_client.get("/api/v1/dashboard/today")
#     assert response.status_code != 401


def test_day_stats_unauthorized(client):
    response = client.get("/api/v1/stats/day?date=2025-12-06")
    assert response.status_code == 401


# def test_day_stats_authorized(authorized_client):
#     response = authorized_client.get("/api/v1/stats/day?date=2025-12-06")
#     assert response.status_code != 401


def test_week_stats_unauthorized(client):
    response = client.get("/api/v1/stats/week?start_date=2025-12-01")
    assert response.status_code == 401


# def test_week_stats_authorized(authorized_client):
#     response = authorized_client.get("/api/v1/stats/week?start_date=2025-12-01")
#     assert response.status_code != 401


def test_month_stats_unauthorized(client):
    response = client.get("/api/v1/stats/month?month=12")
    assert response.status_code == 401


# def test_month_stats_authorized(authorized_client):
#     response = authorized_client.get("/api/v1/stats/month?month=12")
#     assert response.status_code != 401
