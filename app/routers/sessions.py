from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.session import LearningSession
from app.models.user import User
from app.schemas.session import (
    SessionCreate,
    SessionResponse,
    SessionUpdate,
)


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


def check_session_access(
    current_user: User,
    learning_session: LearningSession,
):
    """
    Check whether the current user can access a session.
    """

    # Admin can access everything
    if current_user.role == "admin":
        return

    # Teacher can access only their own sessions
    if current_user.role == "teacher":
        if learning_session.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access another teacher's session",
            )
        return

    # Parent can access only their child's sessions
    if current_user.role == "parent":
        if learning_session.child.parent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot access this session",
            )
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access sessions",
    )


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    session_data: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # Only admins and teachers can create sessions
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can create sessions",
        )

    teacher = db.get(User, session_data.teacher_id)
    child = db.get(User, session_data.child_id)

    if teacher is None or teacher.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid teacher_id",
        )

    if child is None or child.role != "student":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid child_id",
        )

    # A teacher can create sessions only for themselves
    if current_user.role == "teacher":
        if session_data.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers can only create their own sessions",
            )

    new_session = LearningSession(
        title=session_data.title,
        teacher_id=session_data.teacher_id,
        child_id=session_data.child_id,
        scheduled_at=session_data.scheduled_at,
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session


@router.get(
    "",
    response_model=list[SessionResponse],
)
def get_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    query = db.query(LearningSession)

    if current_user.role == "admin":
        return query.all()

    if current_user.role == "teacher":
        return query.filter(
            LearningSession.teacher_id == current_user.id
        ).all()

    if current_user.role == "parent":
        return (
            query.join(
                User,
                LearningSession.child_id == User.id,
            )
            .filter(User.parent_id == current_user.id)
            .all()
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to view sessions",
    )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
)
def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    learning_session = db.get(
        LearningSession,
        session_id,
    )

    if learning_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    check_session_access(
        current_user,
        learning_session,
    )

    return learning_session


@router.put(
    "/{session_id}",
    response_model=SessionResponse,
)
def update_session(
    session_id: int,
    session_data: SessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    learning_session = db.get(
        LearningSession,
        session_id,
    )

    if learning_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    check_session_access(
        current_user,
        learning_session,
    )

    # Parents should not modify sessions
    if current_user.role == "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Parents cannot modify sessions",
        )

    update_data = session_data.model_dump(
        exclude_unset=True
    )

    if "teacher_id" in update_data:
        teacher = db.get(
            User,
            update_data["teacher_id"],
        )

        if teacher is None or teacher.role != "teacher":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid teacher_id",
            )

    if "child_id" in update_data:
        child = db.get(
            User,
            update_data["child_id"],
        )

        if child is None or child.role != "student":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid child_id",
            )

    if current_user.role == "teacher":
        if (
            "teacher_id" in update_data
            and update_data["teacher_id"] != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers cannot assign sessions to another teacher",
            )

    for field, value in update_data.items():
        setattr(
            learning_session,
            field,
            value,
        )

    db.commit()
    db.refresh(learning_session)

    return learning_session


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    learning_session = db.get(
        LearningSession,
        session_id,
    )

    if learning_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    check_session_access(
        current_user,
        learning_session,
    )

    if current_user.role == "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Parents cannot delete sessions",
        )

    db.delete(learning_session)
    db.commit()

    return None