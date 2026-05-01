from src.ai.feature_builder import (
    build_task_features,
    build_priority_features,
    extract_feature_vector
)

from src.ai.model_loader import (
    get_duration_model,
    get_priority_model
)


# =========================================================
# DURATION PREDICTION
# =========================================================

def predict_duration(task, user_stats):
    """
    Predict task duration in hours.
    """

    model = get_duration_model()

    # Safe fallback
    if model is None:
        return getattr(task, "estimated_duration", 1.0)

    features = build_task_features(
        task,
        user_stats
    )

    vector = extract_feature_vector(features)

    prediction = model.predict([vector])[0]

    return max(float(prediction), 0.25)


# =========================================================
# PRIORITY PREDICTION
# =========================================================

def predict_priority(task, user_stats, duration):
    """
    Predict dynamic priority score.
    Higher number = higher priority.
    """

    model = get_priority_model()

    # Safe fallback
    if model is None:
        return getattr(task, "user_importance", 1.0)

    features = build_priority_features(
        task,
        user_stats,
        duration
    )

    vector = extract_feature_vector(features)

    prediction = model.predict([vector])[0]

    return max(float(prediction), 0.1)