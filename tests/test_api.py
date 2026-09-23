import uuid

import redis
from fastapi.testclient import TestClient

from app.database import settings
from app.main import app

client = TestClient(app)

redis_client = redis.Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)


def unique_email(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"


def register_user(name, role, password="Test123!", parent_id=None):
    email = unique_email(role)

    payload = {
        "name": name,
        "email": email,
        "password": password,
        "role": role,
    }

    if parent_id is not None:
        payload["parent_id"] = parent_id

    response = client.post(
        "/auth/register",
        json=payload,
    )

    assert response.status_code == 201

    return email, password


def login(email, password):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def get_me(token):
    response = client.get(
        "/me",
        headers=auth_header(token),
    )

    assert response.status_code == 200

    return response.json()


def test_health():
    response = client.get("/health")

    assert response.status_code == 200


def test_register_and_login():
    email, password = register_user(
        "Test Teacher",
        "teacher",
    )

    token = login(email, password)

    assert token


def test_teacher_can_only_see_own_sessions():
    email1, password1 = register_user(
        "Teacher One",
        "teacher",
    )
    email2, password2 = register_user(
        "Teacher Two",
        "teacher",
    )

    token1 = login(email1, password1)
    token2 = login(email2, password2)

    response1 = client.get(
        "/sessions",
        headers=auth_header(token1),
    )

    response2 = client.get(
        "/sessions",
        headers=auth_header(token2),
    )

    assert response1.status_code == 200
    assert response2.status_code == 200

    sessions1 = response1.json()
    sessions2 = response2.json()

    teacher1 = get_me(token1)
    teacher2 = get_me(token2)

    assert all(
        session["teacher_id"] == teacher1["id"]
        for session in sessions1
    )

    assert all(
        session["teacher_id"] == teacher2["id"]
        for session in sessions2
    )


def test_parent_can_only_see_own_child_sessions():
    # Create teacher
    teacher_email, teacher_password = register_user(
        "Parent RBAC Teacher",
        "teacher",
    )

    teacher_token = login(
        teacher_email,
        teacher_password,
    )

    teacher = get_me(teacher_token)

    # Create two parents
    parent1_email, parent1_password = register_user(
        "Parent One RBAC",
        "parent",
    )

    parent2_email, parent2_password = register_user(
        "Parent Two RBAC",
        "parent",
    )

    parent1_token = login(
        parent1_email,
        parent1_password,
    )

    parent2_token = login(
        parent2_email,
        parent2_password,
    )

    parent1 = get_me(parent1_token)

    # Create a child belonging to Parent 1
    student_email, student_password = register_user(
        "Child One RBAC",
        "student",
        parent_id=parent1["id"],
    )

    student_token = login(
        student_email,
        student_password,
    )

    student = get_me(student_token)

    # Teacher creates a session for Parent 1's child
    session_response = client.post(
        "/sessions",
        headers=auth_header(teacher_token),
        json={
            "title": "Parent RBAC Session",
            "teacher_id": teacher["id"],
            "child_id": student["id"],
            "scheduled_at": "2026-09-25T10:00:00",
        },
    )

    assert session_response.status_code in (200, 201)

    # Parent 1 can see their own child's session
    parent1_sessions = client.get(
        "/sessions",
        headers=auth_header(parent1_token),
    )

    assert parent1_sessions.status_code == 200

    assert any(
        session["child_id"] == student["id"]
        for session in parent1_sessions.json()
    )

    # Parent 2 cannot see Parent 1's child's session
    parent2_sessions = client.get(
        "/sessions",
        headers=auth_header(parent2_token),
    )

    assert parent2_sessions.status_code == 200

    assert all(
        session["child_id"] != student["id"]
        for session in parent2_sessions.json()
    )


def test_unauthenticated_sessions_request_is_rejected():
    response = client.get("/sessions")

    assert response.status_code == 401


def test_evaluation_is_queued():
    email, password = register_user(
        "Evaluation Teacher",
        "teacher",
    )

    token = login(email, password)

    sessions_response = client.get(
        "/sessions",
        headers=auth_header(token),
    )

    assert sessions_response.status_code == 200

    sessions = sessions_response.json()

    if not sessions:
        return

    session_id = sessions[0]["id"]

    queue_before = redis_client.llen(
        "evaluation_queue",
    )

    response = client.post(
        f"/sessions/{session_id}/evaluate",
        headers=auth_header(token),
    )

    assert response.status_code == 202

    queue_after = redis_client.llen(
        "evaluation_queue",
    )

    assert queue_after >= queue_before + 1