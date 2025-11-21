from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root():
    # 루트 경로("/")로 GET 요청
    response = client.get("/")

    # 200 OK 응답 확인
    assert response.status_code == 200

    # 반환된 JSON 내용 확인
    assert response.json() == {"message": "Welcome to Caloreat API", "status": "ok"}
