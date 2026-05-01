from src.db.session import engine
from src.db.models_ai import Base

Base.metadata.create_all(bind=engine)

print("AI tables created")