import json
import unittest
from typing import Any

from mutagen import id3, mp4

from audio_metadata_editor.metadata import AudioType, Metadata


################
##  UNITTEST  ##
################
class TestMetadata(unittest.TestCase):
    # @classmethod
    # def setUpClass(cls) -> None:
    #     """Runs after opening the class"""
    #     return

    # @classmethod
    # def tearDownClass(cls) -> None:
    #     """Runs before closing the class"""
    #     return

    # def setUp(self) -> None:
    #     """Runs before opening each function."""
    #     return

    # def tearDown(self) -> None:
    #     """Runs before closing each function."""
    #     return

    def test_map_metadata(self) -> None:
        """Tests the `Metadata._map_metadata` function."""
        self.assertEqual(Metadata._map_metadata("disk", AudioType.MP4), "disk")
        self.assertEqual(Metadata._map_metadata("", AudioType.MP4), None)
        self.assertEqual(
            Metadata._map_metadata("disk", AudioType.MP3), ("TPOS", id3.TPOS)
        )
        self.assertEqual(Metadata._map_metadata("", AudioType.MP3), None)
        return

    def test_add_to_m4a(self) -> None:
        """Tests the `Metadata.add_to_m4a` function."""
        with open("tests/test_metadata_1.json", encoding="utf-8") as jsonfile:
            audio_data: dict[str, Any] = json.load(jsonfile)

        metadata = Metadata(**audio_data)
        metadata.add_to_m4a("tests/test_audio_1.m4a", autosave=True)

        if not isinstance(metadata.audio, mp4.MP4):
            self.assertFalse(
                isinstance(metadata.audio, mp4.MP4),
                "Audio file is not a mp4/m4a file",
            )
            return

        tags: Any = metadata.audio.tags

        self.assertEqual(
            tags.get(metadata._map_metadata("album", AudioType.MP4)),
            [audio_data["album"]],
        )
        self.assertEqual(
            tags.get(metadata._map_metadata("track", AudioType.MP4)),
            [audio_data["track"]],
        )
        self.assertEqual(
            tags.get(metadata._map_metadata("date", AudioType.MP4)),
            [audio_data["date"]],
        )
        self.assertEqual(
            tags.get(metadata._map_metadata("compilation", AudioType.MP4)),
            audio_data["compilation"],
        )
        self.assertEqual(
            tags.get(metadata._map_metadata("account_id", AudioType.MP4)),
            [audio_data["account_id"]],
        )

        del audio_data
        del metadata
        del tags
        return

    def test_add_to_mp3(self) -> None:
        """Tests the `Metadata.add_to_mp3` function."""
        with open("tests/test_metadata_2.json", encoding="utf-8") as jsonfile:
            audio_data: dict[str, Any] = json.load(jsonfile)

        metadata = Metadata(**audio_data)
        metadata.add_to_mp3("tests/test_audio_2.mp3", autosave=True)

        if not isinstance(metadata.audio, id3.ID3):
            self.assertFalse(
                isinstance(metadata.audio, id3.ID3),
                "Audio file is not a mp3 file",
            )
            return

        self.assertEqual(
            metadata.audio.get(metadata._map_metadata("album", AudioType.MP3)[0]),
            audio_data["album"],
        )
        self.assertEqual(
            metadata.audio.get(metadata._map_metadata("track", AudioType.MP3)[0]),
            "/".join(map(str, audio_data["track"])),
        )
        self.assertEqual(
            metadata.audio.get(metadata._map_metadata("date", AudioType.MP3)[0]),
            audio_data["date"],
        )
        self.assertEqual(
            metadata.audio.get(metadata._map_metadata("account_id", AudioType.MP3)),
            None,
        )

        del audio_data
        del metadata
        return


if __name__ == "__main__":
    unittest.main()
