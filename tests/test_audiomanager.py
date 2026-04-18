from unittest.mock import MagicMock, patch

import pytest

from src.ambient_focus.audiomanager import AudioManager


@pytest.fixture
def manager():
    return AudioManager()


class TestPresets:
    def test_list_all_presets_returns_dict(self, manager):
        presets = manager.list_presets()
        assert isinstance(presets, dict)
        assert len(presets) > 0

    def test_list_presets_by_category(self, manager):
        nature = manager.list_presets(category="nature")
        assert all(v["category"] == "nature" for v in nature.values())

    def test_list_presets_invalid_category_returns_empty(self, manager):
        result = manager.list_presets(category="nonexistent")
        assert result == {}

    def test_play_valid_preset(self, manager):
        manager.play_preset("rain")
        assert manager.active_track is not None
        assert manager.active_track["label"] == "Rainy Day"

    def test_play_invalid_preset_raises_error(self, manager):
        with pytest.raises(ValueError, match="not found"):
            manager.play_preset("doesnt_exist")

    def test_play_preset_sets_active_track(self, manager):
        manager.play_preset("white_noise")
        assert manager.active_track["category"] == "noise"


class TestUploads:
    def test_upload_valid_mp3(self, manager, tmp_path):
        fake_file = tmp_path / "mysong.mp3"
        fake_file.write_bytes(b"fake audio data")
        track_id = manager.upload_track(str(fake_file), label="My Song")
        assert track_id in manager.user_tracks
        assert manager.user_tracks[track_id]["label"] == "My Song"

    def test_upload_uses_filename_as_default_label(self, manager, tmp_path):
        fake_file = tmp_path / "ambient.mp3"
        fake_file.write_bytes(b"fake audio data")
        track_id = manager.upload_track(str(fake_file))
        assert manager.user_tracks[track_id]["label"] == "ambient"

    def test_upload_unsupported_format_raises_error(self, manager, tmp_path):
        bad_file = tmp_path / "video.mp4"
        bad_file.write_bytes(b"fake data")
        with pytest.raises(ValueError, match="Unsupported audio format"):
            manager.upload_track(str(bad_file))

    def test_upload_missing_file_raises_error(self, manager):
        with pytest.raises(FileNotFoundError):
            manager.upload_track("/nonexistent/path/song.mp3")

    def test_upload_supported_formats(self, manager, tmp_path):
        for fmt in ["wav", "ogg", "flac"]:
            fake_file = tmp_path / f"test.{fmt}"
            fake_file.write_bytes(b"fake audio data")
            track_id = manager.upload_track(str(fake_file))
            assert track_id in manager.user_tracks

    def test_play_uploaded_track(self, manager, tmp_path):
        fake_file = tmp_path / "focus.mp3"
        fake_file.write_bytes(b"fake audio data")
        track_id = manager.upload_track(str(fake_file))
        manager.play_user_track(track_id)
        assert manager.active_track["category"] == "user"

    def test_play_nonexistent_user_track_raises_error(self, manager):
        with pytest.raises(ValueError, match="not found"):
            manager.play_user_track("ghost_track")


class TestPlaybackControls:
    def test_stop_clears_active_track(self, manager):
        manager.play_preset("rain")
        manager.stop()
        assert manager.active_track is None

    def test_set_volume_valid(self, manager):
        manager.set_volume(0.5)
        assert manager.volume == 0.5

    def test_set_volume_zero(self, manager):
        manager.set_volume(0.0)
        assert manager.volume == 0.0

    def test_set_volume_max(self, manager):
        manager.set_volume(1.0)
        assert manager.volume == 1.0

    def test_set_volume_out_of_range_raises_error(self, manager):
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            manager.set_volume(1.5)

    def test_set_volume_negative_raises_error(self, manager):
        with pytest.raises(ValueError):
            manager.set_volume(-0.1)

    def test_default_volume_is_set(self, manager):
        assert manager.volume == 0.7


class TestIntegrations:
    @patch("src.ambient_focus.integrations.spotify.SpotifyClient")
    def test_play_spotify_calls_client(self, mock_spotify, manager):
        mock_instance = MagicMock()
        mock_spotify.return_value = mock_instance
        manager.play_from_integration("spotify", "lofi playlist")
        mock_instance.play.assert_called_once_with("lofi playlist")

    @patch("src.ambient_focus.integrations.youtube.YouTubeClient")
    def test_play_youtube_calls_client(self, mock_youtube, manager):
        mock_instance = MagicMock()
        mock_youtube.return_value = mock_instance
        manager.play_from_integration("youtube", "rain sounds")
        mock_instance.play.assert_called_once_with("rain sounds")

    def test_unknown_integration_raises_error(self, manager):
        with pytest.raises(ValueError, match="Unknown integration"):
            manager.play_from_integration("soundcloud", "beats")
