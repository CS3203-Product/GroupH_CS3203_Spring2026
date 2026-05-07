from src.db.session import SessionLocal

from src.ai.task_logger import TaskLogger
from src.ai.behavior_tracker import BehaviorTracker
from src.ai.orchestrator import AIOrchestrator


session = SessionLocal()

task_logger = TaskLogger(session)

behavior_tracker = BehaviorTracker(session)

ai_orchestrator = AIOrchestrator(session)