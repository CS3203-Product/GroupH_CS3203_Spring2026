"""Built-in ambient tracks (paths are served under /assets/sound)."""

PRESETS = {
    "focus_alarm": {
        "label": "Focus alarm (local)",
        "file": "/assets/sound/alarm.mp3",
        "category": "alerts",
        "loop": False,
    },
    "rain": {
        "label": "Rainy Day",
        "file": "/assets/sound/rain.mp3",
        "category": "nature",
        "loop": True,
    },
    "lofi_beats": {
        "label": "Lo-Fi beats",
        "file": "/assets/sound/lofi.mp3",
        "category": "music",
        "loop": True,
    },
    "white_noise": {
        "label": "White noise",
        "file": "/assets/sound/white_noise.mp3",
        "category": "noise",
        "loop": True,
    },
    "cafe": {
        "label": "Coffee shop",
        "file": "/assets/sound/cafe.mp3",
        "category": "ambient",
        "loop": True,
    },
}
