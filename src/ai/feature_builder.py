from datetime import datetime


# =========================================================
# CATEGORY ENCODING
# =========================================================

CATEGORY_MAP = {
    "study": 0,
    "programming": 1,
    "reading": 2,
    "exercise": 3,
    "meeting": 4,
    "general": 5
}


# =========================================================
# FIXED FEATURE ORDER
# VERY IMPORTANT FOR ML CONSISTENCY
# =========================================================

FEATURE_ORDER = [
    "difficulty",
    "importance",
    "category",
    "estimated_duration",
    "hours_until_deadline",
    "deadline_day",
    "deadline_hour",
    "completion_rate",
    "avg_delay",
    "avg_task_duration",
    "overdue_tasks",
    "predicted_duration"
]


# =========================================================
# TASK FEATURE BUILDER
# =========================================================


def build_task_features(task, user_stats=None):
    """
    Builds ML-ready features for task prediction.

    Parameters:
    - task:
        task object from database

    - user_stats:
        UserBehaviorStats object
    """

    now = datetime.utcnow()

    # =====================================================
    # SAFE DEADLINE CALCULATION
    # =====================================================

    hours_until_deadline = 72
    deadline_day = 0
    deadline_hour = 12

    if getattr(task, "deadline", None):

        delta = task.deadline - now

        hours_until_deadline = (
            delta.total_seconds() / 3600
        )

        deadline_day = task.deadline.weekday()
        deadline_hour = task.deadline.hour

    # Prevent extreme negative values
    hours_until_deadline = max(
        hours_until_deadline,
        -72
    )

    # =====================================================
    # CATEGORY ENCODING
    # =====================================================

    category = CATEGORY_MAP.get(
        getattr(task, "category", "general"),
        CATEGORY_MAP["general"]
    )

    # =====================================================
    # BASE FEATURES
    # =====================================================

    features = {
        "difficulty": float(
            getattr(task, "difficulty", 5)
        ),

        "importance": float(
            getattr(task, "user_importance", 5)
        ),

        "category": float(category),

        "estimated_duration": float(
            getattr(task, "estimated_duration", 1)
        ),

        "hours_until_deadline": float(
            hours_until_deadline
        ),

        "deadline_day": float(deadline_day),

        "deadline_hour": float(deadline_hour),

        # Default placeholders
        "completion_rate": 0.5,
        "avg_delay": 0.0,
        "avg_task_duration": 1.0,
        "overdue_tasks": 0,

        # Only used in priority model
        "predicted_duration": 1.0
    }

    # =====================================================
    # USER BEHAVIOR FEATURES
    # =====================================================

    if user_stats:

        features.update({
            "completion_rate": float(
                getattr(user_stats, "completion_rate", 0.5)
            ),

            "avg_delay": float(
                getattr(user_stats, "avg_delay", 0)
            ),

            "avg_task_duration": float(
                getattr(user_stats, "avg_task_duration", 1)
            ),

            "overdue_tasks": float(
                getattr(user_stats, "overdue_tasks", 0)
            )
        })

    return features


def build_priority_features(
    task,
    user_stats,
    predicted_duration
):
    """
    Build feature dictionary for priority prediction.
    
    Args:
        task: Task object
        user_stats: User statistics
        duration: Predicted duration
    
    Returns:
        Dictionary of features for priority model
    """
    features = build_task_features(
        task,
        user_stats
    )

    features["predicted_duration"] = float(
        predicted_duration
    )

    return features


# =========================================================
# FEATURE VECTOR EXTRACTION
# =========================================================


def extract_feature_vector(features):
    """
    Converts feature dictionary into
    ordered ML vector.
    """

    vector = []

    for feature_name in FEATURE_ORDER:

        value = features.get(feature_name, 0)

        try:
            vector.append(float(value))

        except Exception:
            vector.append(0.0)

    return vector


def extract_priority_vector(features):
    """
    Compatibility wrapper for priority vector extraction.
    """

    return extract_feature_vector(features)
