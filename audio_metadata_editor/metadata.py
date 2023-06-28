# @title # Required audio metadata class { display-mode: "form", run: "auto" }
import os
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional, Union

from mutagen import id3, mp4


class AudioType(Enum):
    MP3 = "mp3"
    MP4 = "mp4"


class Compilation(Enum):
    NO = "0"
    YES = "1"


class MediaType(Enum):
    MOVIE_OLD = "0"
    MUSIC = "1"
    AUDIOBOOK = "2"
    WHACKED_BOOKMARK = "5"
    MUSIC_VIDEO = "6"
    MOVIE = "9"
    TV_SHOW = "10"
    BOOKLET = "11"
    RINGTONE = "14"
    PODCAST = "21"
    ITUNES_U = "23"


class Rating(Enum):
    NONE = "0"
    EXPLICIT = "1"
    CLEAN = "2"
    EXPLICIT_OLD = "4"


@dataclass()
class Metadata:
    """Metadata class for audio files.

    Attributes
    ----------
    audio : Optional[mp4.MP4 | id3.ID3]
        The audio file's metadata object (MP4 or ID3).
    title : Optional[str]
        The title of the audio.
    album : Optional[str]
        The album of the audio.
    album_artist : Optional[str]
        The album artist of the audio.
    artist : Optional[str]
        The artist of the audio.
    track : Optional[tuple[int, int]]
        The track number and total tracks of the audio.
    date : Optional[str]
        The date of the audio.
    genre : Optional[str]
        The genre of the audio.
    composer : Optional[str]
        The composer of the audio.
    disk : tuple[int, int]
        The disk number and total disks of the audio.
    compilation : Optional[int]
        The compilation flag of the audio.
    gapless_playback : Optional[int]
        The gapless playback flag of the audio.
    rating : int
        The rating of the audio.
    media_type : int
        The media type of the audio.
    copyright : Optional[str]
        The copyright information of the audio.
    account_id : Optional[str]
        The account ID of the audio.
    purchase_date : Optional[str]
        The purchase date of the audio.
    sort_name : Optional[str]
        The sorted name of the audio.
    sort_album : Optional[str]
        The sorted album name of the audio.
    sort_album_artist : Optional[str]
        The sorted album artist name of the audio.
    sort_artist : Optional[str]
        The sorted artist name of the audio.
    sort_composer : Optional[str]
        The sorted composer name of the audio.
    lyrics : Optional[str]
        The lyrics of the audio.
    album_art : Optional[str | id3.APIC | mp4.MP4Cover]
        The album art of the audio.
    comment : Optional[str]
        The comment of the audio.

    Methods
    -------
    add_to_m4a(audio: str, autosave: bool = False) -> None
        Add the metadata to an M4A audio file.
    add_to_mp3(audio: str, autosave: bool = False) -> None
        Add the metadata to an MP3 audio file.
    """

    audio: Union[mp4.MP4, id3.ID3, None] = field(default=None)
    title: Optional[str] = field(default=None)
    album: Optional[str] = field(default=None)
    album_artist: Optional[str] = field(default=None)
    artist: Optional[str] = field(default=None)
    track: Optional[tuple[int, int]] = field(default=None)
    date: Optional[str] = field(default=None)
    genre: Optional[str] = field(default=None)
    composer: Optional[str] = field(default=None)
    disk: tuple[int, int] = field(default_factory=lambda: (1, 1))
    compilation: Optional[int] = field(default=None)
    gapless_playback: Optional[int] = field(default=None)
    rating: int = field(default=int(Rating.NONE.value))
    media_type: int = field(default=int(MediaType.MUSIC.value))
    copyright: Optional[str] = field(default=None)
    account_id: Optional[str] = field(default=None)
    purchase_date: Optional[str] = field(default=None)
    sort_name: Optional[str] = field(default=None)
    sort_album: Optional[str] = field(default=None)
    sort_album_artist: Optional[str] = field(default=None)
    sort_artist: Optional[str] = field(default=None)
    sort_composer: Optional[str] = field(default=None)
    lyrics: Optional[str] = field(default=None)
    album_art: Union[str, id3.APIC, mp4.MP4Cover, None] = field(default=None)
    comment: Optional[str] = field(default=None)

    @staticmethod
    def _map_metadata(key: str, type: AudioType) -> Any:
        """Map the metadata key to the corresponding tag and metadata object.

        Parameters
        ----------
        key : str
            The metadata key.
        type : AudioType
            The audio type (MP4 or MP3).

        Returns
        -------
        Any
            The corresponding tag and metadata object.
        """
        if key not in (
            "title",
            "album",
            "album_artist",
            "artist",
            "track",
            "date",
            "genre",
            "composer",
            "disk",
            "compilation",
            "gapless_playback",
            "rating",
            "media_type",
            "copyright",
            "account_id",
            "purchase_date",
            "sort_name",
            "sort_album",
            "sort_album_artist",
            "sort_artist",
            "sort_composer",
            "lyrics",
            "album_art",
            "comment",
        ):
            return

        return {
            "title": {
                AudioType.MP4: "\xa9nam",
                AudioType.MP3: ("TIT2", id3.TIT2),
            },
            "album": {
                AudioType.MP4: "\xa9alb",
                AudioType.MP3: ("TALB", id3.TALB),
            },
            "album_artist": {
                AudioType.MP4: "aART",
                AudioType.MP3: ("TPE2", id3.TPE2),
            },
            "artist": {
                AudioType.MP4: "\xa9ART",
                AudioType.MP3: ("TPE1", id3.TPE1),
            },
            "track": {
                AudioType.MP4: "trkn",  # (track_number, total_tracks)
                AudioType.MP3: ("TRCK", id3.TRCK),
            },
            "date": {
                AudioType.MP4: "\xa9day",
                AudioType.MP3: ("TDRC", id3.TDRC),
            },
            "genre": {
                AudioType.MP4: "\xa9gen",
                AudioType.MP3: ("TCON", id3.TCON),
            },
            "composer": {
                AudioType.MP4: "\xa9wrt",
                AudioType.MP3: ("TCOM", id3.TCOM),
            },
            "disk": {
                AudioType.MP4: "disk",  # (track_number, total_tracks)
                AudioType.MP3: ("TPOS", id3.TPOS),
            },
            "compilation": {
                AudioType.MP4: "cpil",
                AudioType.MP3: ("TCMP", id3.TCMP),
            },
            "gapless_playback": {
                AudioType.MP4: "pgap",
                AudioType.MP3: None,
            },
            "rating": {
                AudioType.MP4: "rtng",
                AudioType.MP3: None,
            },
            "media_type": {
                AudioType.MP4: "stik",
                AudioType.MP3: None,
            },
            "copyright": {
                AudioType.MP4: "cprt",
                AudioType.MP3: ("TCOP", id3.TCOP),
            },
            "account_id": {
                AudioType.MP4: "apID",
                AudioType.MP3: None,
            },
            "purchase_date": {
                AudioType.MP4: "purd",
                AudioType.MP3: None,
            },
            "sort_name": {
                AudioType.MP4: "sonm",
                AudioType.MP3: ("TSOT", id3.TSOT),
            },
            "sort_album": {
                AudioType.MP4: "soal",
                AudioType.MP3: ("TSOA", id3.TSOA),
            },
            "sort_album_artist": {
                AudioType.MP4: "soaa",
                AudioType.MP3: ("TSO2", id3.TSO2),
            },
            "sort_artist": {
                AudioType.MP4: "soar",
                AudioType.MP3: ("TSOP", id3.TSOP),
            },
            "sort_composer": {
                AudioType.MP4: "soco",
                AudioType.MP3: ("TSOC", id3.TSOC),
            },
            "lyrics": {
                AudioType.MP4: "\xa9lyr",
                AudioType.MP3: ("USLT", id3.USLT),
            },
            "album_art": {
                AudioType.MP4: "covr",
                AudioType.MP3: ("APIC", id3.APIC),
            },
            "comment": {
                AudioType.MP4: "\xa9cmt",
                AudioType.MP3: ("COMM", id3.COMM),
            },
        }[key][type]

    def add_to_m4a(self, audio: str, autosave: bool = False) -> None:
        """Add the metadata to an M4A audio file.

        Parameters
        ----------
        audio : str
            The path to the M4A audio file.
        autosave : bool, optional
            Whether to save the changes to the audio file automatically, by default False.
        """
        if self.album_art and isinstance(self.album_art, str):
            # IMPROVEMENT: instead of loading local image, get the bytes from the url
            # then use the bytes directly to set the album_art

            # open image as bytes
            album_art = self.album_art
            with open(self.album_art, "rb") as image:
                self.album_art = mp4.MP4Cover(data=image.read())
            os.remove(album_art)

        audio_ = mp4.MP4(audio)

        for key, value in asdict(self).items():
            if value is not None and self._map_metadata(key, AudioType.MP4) is not None:
                audio_[self._map_metadata(key, AudioType.MP4)] = [value]

        if autosave:
            audio_.save()
        return

    def add_to_mp3(self, audio: str, autosave: bool = False) -> None:
        """
        Add the metadata to an MP3 audio file.

        Parameters
        ----------
        audio : str
            The path to the MP3 audio file.
        autosave : bool, optional
            Whether to save the changes to the audio file automatically, by default False.
        """
        if self.album_art and isinstance(self.album_art, str):
            # IMPROVEMENT: instead of loading local image, get the bytes from the url
            # then use the bytes directly to set the album_art

            # open image as bytes
            album_art = self.album_art
            with open(self.album_art, "rb") as image:
                self.album_art = id3.APIC(
                    encoding=3, mime="image/jpeg", type=0, data=image.read()
                )
            os.remove(album_art)

        audio_ = id3.ID3(audio)

        for key, value in asdict(self).items():
            if value is None or self._map_metadata(key, AudioType.MP3) is None:
                continue

            tag, metadata = self._map_metadata(key, AudioType.MP3)

            if key in ("track", "disk"):
                # track_disk_number : str/str
                audio_[tag] = metadata(encoding=3, text="/".join(map(str, value)))
            elif key in ("album_art",):
                # album_art : encoding=3, mime='image/jpeg', type=0, desc='Cover',
                # data=open('path/to/album_art.jpg', 'rb').read()
                # NOTE: album cover is added successfully, windows cannot display that.
                audio_[tag] = value
            elif key in ("comment",):
                # comment : encoding=3, desc='sort_name', text='Sort Name'
                # NOTE: comment is added successfully, iTunes cannot display that.
                audio_[tag] = metadata(encoding=3, desc=value, text=value)
            elif isinstance(
                metadata(), (id3.TXXX, id3.TSOT, id3.TSOA, id3.TSO2, id3.TSOP, id3.TSOC)
            ):
                # encoding=3, desc='sort_name', text='Sort Name'
                audio_[tag] = metadata(encoding=3, desc=key, text=value)
            elif key in ("lyrics",):
                # lyrics : encoding=3, text='Sort Name'
                audio_[tag] = metadata(encoding=3, text=value)
            else:
                audio_[tag] = metadata(encoding=3, text=str(value))

        if autosave:
            audio_.save()
        return
