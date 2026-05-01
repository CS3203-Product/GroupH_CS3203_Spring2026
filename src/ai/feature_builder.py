"""
Feature Builder for AI models.

Builds feature vectors from task and user data for ML inference.
"""

from datetime import datetime
from typing import Dict, Any, Optional


def build_task_features(task, user_stats: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Build feature dictionary from a task.
    
    Args:
        task: Task object with attributes
        user_stats: Optional user statistics dict
    
    Returns:
        Dictionary of features for ML model
    """
    features = {}
    
    # Task properties
    features["task_id"] = getattr(task, "id", 0)
    features["user_id"] = getattr(task, "user_id", 0)
    features["estimated_duration"] = getattr(task, "estimated_duration", 1.0)
    features["user_importance"] = getattr(task, "user_importance", 1.0)
    features["difficulty"] = getattr(task, "difficulty", 3)
    
    # Category encoding
    category = getattr(task, "category", "general")
    features["category_encoded"] = _encode_category(category)
    
    # Time-based features
    now = datetime.utcnow()
    deadline = getattr(task, "deadline", now)
    
    if deadline:
        delta = deadline - now
        hours_until_deadline = delta.total_seconds() / 3600
    else:
        hours_until_deadline = 24.0
    
    features["hours_until_deadline"] = max(hours_until_deadline, 0.1)
    features["deadline_day"] = deadline.weekday() if hasattr(deadline, "weekday") else 0
    features["deadline_hour"] = getattr(deadline, "hour", 12) if hasattr(deadline, "hour") else 12
    
    # User stats features
    if user_stats:
        features["user_completion_rate"] = user_stats.get("completion_rate", 0.5)
        features["user_avg_delay"] = user_stats.get("avg_delay", 0.0)
        features["user_avg_duration"] = user_stats.get("avg_task_duration", 1.0)
        features["user_overdue_tasks"] = user_stats.get("overdue_tasks", 0)
    else:
        features["user_completion_rate"] = 0.5
        features["user_avg_delay"] = 0.0
        features["user_avg_duration"] = 1.0
        features["user_overdue_tasks"] = 0
    
    return features


def build_priority_features(task, user_stats: Optional[Dict], duration: float) -> Dict[str, Any]:
    """
    Build feature dictionary for priority prediction.
    
    Args:
        task: Task object
        user_stats: User statistics
        duration: Predicted duration
    
    Returns:
        Dictionary of features for priority model
    """
    features = build_task_features(task, user_stats)
    
    # Add duration-related features
    features["predicted_duration"] = duration
    
    # Workload features
    now = datetime.utcnow()
    deadline = getattr(task, "deadline", now)
    
    if hasattr(deadline, "total_seconds"):
        hours_left = deadline.total_seconds() / 3600
    else:
        hours_left = 24.0
    
    features["workload_ratio"] = duration / max(hours_left, 0.1)
    features["urgency_score"] = 1.0 / max(hours_left, 1.0)
    
    return features


def _encode_category(category: str) -> int:
    """Encode category string to integer."""
    category_map = {
        "study": 0,
        "homework": 1,
        "project": 2,
        "exam": 3,
        "reading": 4,
        "practice": 5,
        "review": 6,
        "general": 7
    }
    return category_map.get(category.lower(), 7)


def extract_feature_vector(features: Dict[str, Any]) -> list:
    """
    Extract ordered feature vector for model input.
    
    Args:
        features: Feature dictionary
    
    Returns:
        List of features in order
    """
    key_order = [
        "estimated_duration",
        "user_importance",
        "difficulty",
        "category_encoded",
        "hours_until_deadline",
        "deadline_day",
        "deadline_hour",
        "user_completion_rate",
        "user_avg_delay",
        "user_avg_duration",
        "user_overdue_tasks"
    ]
    
    return [features.get(key, 0.0) for key in key_order]


def extract_priority_vector(features: Dict[str, Any]) -> list:
    """
    Extract ordered feature vector for priority model.
    
    Args:
        features: Feature dictionary
    
    Returns:
        List of features in order
    """
    key_order = [
        "estimated_duration",
        "user_importance",
        "difficulty",
        "category_encoded",
        "hours_until_deadline",
        "deadline_day",
        "deadline_hour",
        "user_completion_rate",
        "user_avg_delay",
        "user_avg_duration",
        "user_overdue_tasks",
        "predicted_duration",
        "workload_ratio",
        "urgency_score"
    ]
    
    return [features.get(key, 0.0) for key in key_order]