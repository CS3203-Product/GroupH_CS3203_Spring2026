from pathlib import Path

from src.ambient_focus.presets import PRESETS


class AudioManager:
    def __init__(self) -> None:
        self.presets = PRESETS
        self.user_tracks: dict = {}
        self.active_track = None
        self.volume = 0.7

    def list_presets(self, category=None):
        if category:
            return {k: v for k, v in self.presets.items() if v["category"] == category}
        return self.presets

    def play_preset(self, key: str) -> None:
        if key not in self.presets:
            raise ValueError(f"Preset '{key}' not found.")
        self.active_track = self.presets[key]
        print(f"Playing preset: {self.active_track['label']}")

    def upload_track(self, filepath: str, label: str | None = None) -> str:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        if path.suffix.lower() not in {".mp3", ".wav", ".ogg", ".flac"}:
            raise ValueError("Unsupported audio format.")
        track_id = path.stem
        self.user_tracks[track_id] = {
            "label": label or path.stem,
            "file": str(path),
            "category": "user",
            "loop": False,
        }
        print(f"Uploaded: {self.user_tracks[track_id]['label']}")
        return track_id

    def play_user_track(self, track_id: str) -> None:
        if track_id not in self.user_tracks:
            raise ValueError(f"Track '{track_id}' not found.")
        self.active_track = self.user_tracks[track_id]
        print(f"Playing: {self.active_track['label']}")

    def play_from_integration(self, source: str, query: str) -> None:
        if source == "spotify":
            from src.ambient_focus.integrations.spotify import SpotifyClient

            client = SpotifyClient()
            client.play(query)
        elif source == "youtube":
            from src.ambient_focus.integrations.youtube import YouTubeClient

            client = YouTubeClient()
            client.play(query)
        else:
            raise ValueError(f"Unknown integration: {source}")

    def stop(self) -> None:
        self.active_track = None
        print("Playback stopped.")

    def set_volume(self, level: float) -> None:
        if not 0.0 <= level <= 1.0:
            raise ValueError("Volume must be between 0.0 and 1.0")
        self.volume = level
        print(f"Volume set to {int(level * 100)}%")
