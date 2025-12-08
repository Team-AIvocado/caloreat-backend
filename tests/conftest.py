import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from main import app
from app.db.database import get_db
from app.core.auth import get_current_user, get_user_id
from app.db.models.user import User
from datetime import datetime, timezone

# Mock DB Session
@pytest.fixture
def mock_db_session():
    return AsyncMock()

# Override get_db dependency
@pytest.fixture
def override_get_db(mock_db_session):
    async def _get_db():
        yield mock_db_session
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.pop(get_db, None)

# Mock Current User
@pytest.fixture
def mock_current_user():
    user = User(
        id=1,
        email="test@example.com",
        username="testuser",
        nickname="Test User",
        password="hashedpassword",
        created_at=datetime.now(timezone.utc), # Added created_at
        is_active=True,
        email_verified=False
    )
    return user

@pytest.fixture
def override_get_current_user(mock_current_user):
    async def _get_current_user():
        return mock_current_user
    app.dependency_overrides[get_current_user] = _get_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)

@pytest.fixture
def override_get_user_id(mock_current_user):
    async def _get_user_id():
        return mock_current_user.id
    app.dependency_overrides[get_user_id] = _get_user_id
    yield
    app.dependency_overrides.pop(get_user_id, None)

# Test Client
@pytest.fixture
def client(override_get_db):
    return TestClient(app)

# Authorized Client
@pytest.fixture
def authorized_client(client, override_get_current_user, override_get_user_id):
    return client

# Mock Services
@pytest.fixture
def mock_user_service():
    with patch("app.routers.user.UserService", autospec=True) as mock:
        yield mock

@pytest.fixture
def mock_user_crud():
    with patch("app.routers.user.UserCrud", autospec=True) as mock:
        yield mock

@pytest.fixture
def mock_health_condition_service():
    with patch("app.routers.user_health_condition.HealthConditionService", autospec=True) as mock:
        yield mock

@pytest.fixture
def mock_user_profile_service():
    with patch("app.routers.user_profile.UserProfileService", autospec=True) as mock:
        yield mock

@pytest.fixture
def mock_profile_form_service():
    with patch("app.routers.user_profile_form.ProfileFormService", autospec=True) as mock:
        yield mock
