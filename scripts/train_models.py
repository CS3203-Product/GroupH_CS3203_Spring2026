from src.db.session import SessionLocal

from src.ai.retrain import retrain_all_models


session = SessionLocal()

retrain_all_models(session)

print("AI training complete")