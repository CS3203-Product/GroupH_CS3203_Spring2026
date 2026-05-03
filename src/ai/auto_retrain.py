"""Auto-retrain models in background after task completion."""

import threading
import subprocess
import sys
from pathlib import Path


# Track if retraining is in progress to avoid redundant retrains
_retraining = False


def trigger_background_retrain():
    """
    Trigger model retraining by running the train_models.py script in a background thread.
    Non-blocking - returns immediately.
    """
    global _retraining
    
    # Only one retrain at a time
    if _retraining:
        return
    
    def _retrain_worker():
        global _retraining
        try:
            _retraining = True
            script_path = Path(__file__).resolve().parent.parent.parent / "scripts" / "train_models.py"
            
            # Run the training script as a subprocess
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print("[AUTO-RETRAIN] Models retrained successfully in background")
            else:
                print(f"[AUTO-RETRAIN] Error retraining models: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("[AUTO-RETRAIN] Retraining timed out after 5 minutes")
        except Exception as e:
            print(f"[AUTO-RETRAIN] Error running retrain script: {e}")
        finally:
            _retraining = False
    
    # Start retraining in background thread
    thread = threading.Thread(target=_retrain_worker, daemon=True)
    thread.start()

