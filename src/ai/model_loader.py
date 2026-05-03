from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "saved_models"


class ModelLoader:
    """
    Centralized model loading system.

    Handles:
    - duration model
    - priority model
    - future ML models
    """

    _cache = {}

    @classmethod
    def load_model(cls, model_name: str):

        if model_name in cls._cache:
            return cls._cache[model_name]

        model_path = MODEL_DIR / f"{model_name}.pkl"

        if not model_path.exists():
            print(f"[AI] Model not found: {model_path}")
            return None

        try:
            model = joblib.load(model_path)
            cls._cache[model_name] = model

            print(f"[AI] Loaded model: {model_name}")

            return model

        except Exception as e:
            print(f"[AI] Failed to load model {model_name}: {e}")
            return None


# Convenience helpers

def get_duration_model():
    return ModelLoader.load_model("duration_model")


def get_priority_model():
    return ModelLoader.load_model("priority_model")