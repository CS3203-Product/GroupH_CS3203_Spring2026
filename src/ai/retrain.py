from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor

from src.ai.feature_builder import (
    build_task_features,
    build_priority_features,
    extract_feature_vector
)

from src.db.models_ai import TaskExecutionLog


MODEL_DIR = Path(__file__).resolve().parent / "saved_models"
MODEL_DIR.mkdir(exist_ok=True)

# =========================================================
# TRAIN DURATION MODEL
# =========================================================

def train_duration_model(session):

    logs = session.query(TaskExecutionLog).all()

    if len(logs) < 10:
        print("[AI] Not enough data to train duration model")
        return

    X = []
    y = []

    for log in logs:

        fake_task = type("Task", (), {
            "estimated_duration": log.actual_duration,
            "user_importance": 5,
            "difficulty": 3,
            "category": "general",
            "deadline": log.end_time,
            "user_id": log.user_id
        })()

        features = build_task_features(fake_task)

        X.append(extract_feature_vector(features))
        y.append(log.actual_duration)

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    model.fit(X, y)

    save_path = MODEL_DIR / "duration_model.pkl"

    joblib.dump(model, save_path)

    print("[AI] Duration model trained")

# =========================================================
# TRAIN PRIORITY MODEL
# =========================================================

def train_priority_model(session):

    logs = session.query(TaskExecutionLog).all()

    if len(logs) < 10:
        print("[AI] Not enough data to train priority model")
        return

    X = []
    y = []

    for log in logs:

        fake_task = type("Task", (), {
            "estimated_duration": log.actual_duration,
            "user_importance": 5,
            "difficulty": 3,
            "category": "general",
            "deadline": log.end_time,
            "user_id": log.user_id
        })()

        duration = log.actual_duration

        features = build_priority_features(
            fake_task,
            None,
            duration
        )

        X.append(extract_feature_vector(features))

        # Example target:
        # delayed tasks should have higher priority
        target_priority = 10 if log.was_delayed else 5

        y.append(target_priority)

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    model.fit(X, y)

    save_path = MODEL_DIR / "priority_model.pkl"

    joblib.dump(model, save_path)

    print("[AI] Priority model trained")


# =========================================================
# MASTER RETRAIN
# =========================================================

def retrain_all_models(session):

    train_duration_model(session)
    train_priority_model(session)

    print("[AI] All models retrained")