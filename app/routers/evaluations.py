import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.evaluation import Evaluation
from app.models.session import LearningSession
from app.models.user import User
from app.schemas.evaluation import EvaluationResponse
from app.services.redis import redis_client

router = APIRouter(
    prefix="/sessions",
    tags=["Evaluations"],
)


@router.post(
    "/{session_id}/evaluate",
    response_model=EvaluationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def trigger_evaluation(
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

    # Only admin or the teacher who owns the session
    # can trigger an evaluation.
    if current_user.role == "teacher":
        if learning_session.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot evaluate another teacher's session",
            )

    elif current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and session teachers can trigger evaluations",
        )

    evaluation = Evaluation(
        session_id=session_id,
        status="queued",
    )

    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    job = {
        "evaluation_id": evaluation.id,
        "session_id": session_id,
    }

    redis_client.rpush(
        "evaluation_queue",
        json.dumps(job),
    )

    return evaluation