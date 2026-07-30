import pytest
import uuid
from app.models.user import User
from app.models.project import Project
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository
from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_user_persistence.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_create_user(db_session):
    repo = UserRepository(db_session)
    user_in = UserCreate(
        full_name="Test User",
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    user = repo.create(user_in, "hashed_password_123")
    
    assert user.id is not None
    assert user.full_name == "Test User"
    assert user.email == "test@example.com"
    assert user.password_hash == "hashed_password_123"
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.deleted_at is None

def test_get_user_by_email_and_username(db_session):
    repo = UserRepository(db_session)
    user_in = UserCreate(
        full_name="Test User 2",
        email="test2@example.com",
        username="testuser2",
        password="password123"
    )
    created_user = repo.create(user_in, "hashed_password_123")
    
    by_email = repo.get_by_email("test2@example.com")
    by_username = repo.get_by_username("testuser2")
    
    assert by_email is not None
    assert by_username is not None
    assert by_email.id == created_user.id
    assert by_username.id == created_user.id

def test_update_user(db_session):
    repo = UserRepository(db_session)
    user_in = UserCreate(
        full_name="Update User",
        email="update@example.com",
        username="updateuser",
        password="password123"
    )
    created_user = repo.create(user_in, "hash")
    
    update_data = UserUpdate(full_name="Updated Name")
    updated = repo.update(created_user.id, update_data)
    
    assert updated.full_name == "Updated Name"
    assert updated.email == "update@example.com"

def test_soft_delete_user(db_session):
    repo = UserRepository(db_session)
    user_in = UserCreate(
        full_name="Delete User",
        email="delete@example.com",
        username="deleteuser",
        password="password123"
    )
    created_user = repo.create(user_in, "hash")
    
    # Soft delete
    assert repo.soft_delete(created_user.id) is True
    
    # Should not be retrievable by normal gets
    assert repo.get_by_id(created_user.id) is None
    assert repo.get_by_email("delete@example.com") is None
    assert repo.get_by_username("deleteuser") is None
    
    # But should still exist in DB
    stmt = select(User).where(User.id == created_user.id)
    db_user = db_session.execute(stmt).scalar_one_or_none()
    assert db_user is not None
    assert db_user.deleted_at is not None

def test_user_project_relationship(db_session):
    repo = UserRepository(db_session)
    user_in = UserCreate(
        full_name="Relation User",
        email="relation@example.com",
        username="relationuser",
        password="password123"
    )
    user = repo.create(user_in, "hash")
    
    # Create project linked to user
    project = Project(
        name="Test Project",
        user_id=user.id
    )
    db_session.add(project)
    db_session.commit()
    
    # Refresh user to load relationship
    db_session.refresh(user)
    
    assert len(user.projects) == 1
    assert user.projects[0].name == "Test Project"
    assert user.projects[0].user_id == user.id
    assert project.user.id == user.id
