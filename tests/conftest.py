from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.database import Base, get_db_session
from app.main import app
from app.core.security import create_access_token, hash_password
from app.models.user import User
from app.models.profile import UserProfile

TEST_DATABASE_URL = "sqlite:///./test_housing.db"

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db_session():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session: Session) -> User:
    user = db_session.query(User).filter(User.email == "test_admin@housing.com").first()
    if not user:
        user = User(
            email="test_admin@housing.com",
            username="test_admin",
            full_name="Test Administrator",
            role="ADMIN",
            hashed_password=hash_password("Password@123"),
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def landlord_user(db_session: Session) -> User:
    user = db_session.query(User).filter(User.email == "test_landlord@housing.com").first()
    if not user:
        user = User(
            email="test_landlord@housing.com",
            username="test_landlord",
            full_name="Test Landlord",
            role="LANDLORD",
            hashed_password=hash_password("Password@123"),
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def seeker_user(db_session: Session) -> User:
    user = db_session.query(User).filter(User.email == "test_seeker@housing.com").first()
    if not user:
        user = User(
            email="test_seeker@housing.com",
            username="test_seeker",
            full_name="Test Seeker",
            role="ROOMMATE_SEEKER",
            hashed_password=hash_password("Password@123"),
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        db_session.flush()
        profile = UserProfile(
            user_id=user.id,
            bio="Quiet professional.",
            budget_min=8000.0,
            budget_max=14000.0,
            preferred_city="Dhaka",
            cleanliness_level="VERY_CLEAN",
            sleep_schedule="EARLY_BIRD",
            smoking_habit="NON_SMOKER",
            pet_habit="PET_FRIENDLY",
            party_habit="RARELY"
        )
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def candidate_seeker_user(db_session: Session) -> User:
    user = db_session.query(User).filter(User.email == "candidate_seeker@housing.com").first()
    if not user:
        user = User(
            email="candidate_seeker@housing.com",
            username="candidate_seeker",
            full_name="Candidate Seeker",
            role="ROOMMATE_SEEKER",
            hashed_password=hash_password("Password@123"),
            is_active=True,
            is_verified=True
        )
        db_session.add(user)
        db_session.flush()
        profile = UserProfile(
            user_id=user.id,
            bio="Fellow professional.",
            budget_min=8500.0,
            budget_max=14500.0,
            preferred_city="Dhaka",
            cleanliness_level="VERY_CLEAN",
            sleep_schedule="EARLY_BIRD",
            smoking_habit="NON_SMOKER",
            pet_habit="PET_FRIENDLY",
            party_habit="RARELY"
        )
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def admin_auth_headers(admin_user: User) -> dict:
    token = create_access_token(str(admin_user.id), {"role": admin_user.role, "username": admin_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def landlord_auth_headers(landlord_user: User) -> dict:
    token = create_access_token(str(landlord_user.id), {"role": landlord_user.role, "username": landlord_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seeker_auth_headers(seeker_user: User) -> dict:
    token = create_access_token(str(seeker_user.id), {"role": seeker_user.role, "username": seeker_user.username})
    return {"Authorization": f"Bearer {token}"}
