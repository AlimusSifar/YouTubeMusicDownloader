from audio_metadata_editor.metadata import AudioType, MediaType, Metadata
from audio_metadata_editor.spotify_api import SpotifyAPI
from audio_metadata_editor.youtube_audio_downloader import YouTubeAudioDownloader

version_tuple: tuple[int, int, int] = (1, 0, 0)  # (main, minor, patchlevel)
version: str = ".".join(map(str, version_tuple))

YTAD = YouTubeAudioDownloader


__all__: list[str] = [
    "AudioType",
    "MediaType",
    "Metadata",
    "SpotifyAPI",
    "YouTubeAudioDownloader",
    "YTAD",
]
