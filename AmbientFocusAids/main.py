from audio_manager import AudioManager

if __name__ == "__main__":
    manager = AudioManager()

    print("=== Available Presets ===")
    for key, track in manager.list_presets().items():
        print(f"  [{key}] {track['label']} ({track['category']})")

    manager.play_preset("rain")
    manager.set_volume(0.8)
```

**`requirements.txt`** — start lean, expand as you add integrations:
```
pygame>=2.5.0        # local audio playback
spotipy>=2.23.0      # Spotify (optional, wire up later)
yt-dlp>=2024.1.0     # YouTube audio (optional)