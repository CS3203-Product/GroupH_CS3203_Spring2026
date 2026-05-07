
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
from src.db.session import SessionLocal

from src.ai.retrain import retrain_all_models


session = SessionLocal()

retrain_all_models(session)

print("AI training complete")