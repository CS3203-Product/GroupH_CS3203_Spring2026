from fastapi import APIRouter

from src.ai.orchestrator import AIOrchestrator
from src.db.session import SessionLocal

router = APIRouter()


@router.post("/schedule")
def build_schedule():

    session = SessionLocal()

    ai = AIOrchestrator(session)

    tasks = []

    scheduled = ai.schedule_tasks(tasks)

    session.commit()

    return {
        "scheduled": len(scheduled)
    }