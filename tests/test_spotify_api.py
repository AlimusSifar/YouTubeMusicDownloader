import os
import unittest

from audio_metadata_editor.spotify_api import SpotifyAPI


################
##  UNITTEST  ##
################
class TestSpotifyAPI(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        """Runs before closing the class"""
        os.remove("tests/auth_test_1.json")
        os.remove("tests/auth_test_2.json")
        return

    def setUp(self) -> None:
        """Runs before opening each function."""
        self.spotify = SpotifyAPI()
        return

    def tearDown(self) -> None:
        """Runs before closing each function."""
        del self.spotify
        return

    def test_is_authenticated(self) -> None:
        """Tests the `SpotifyAPI.is_authenticated` function."""

        self.assertFalse(self.spotify.is_authenticated("tests/auth_test_1.json"))
        self.assertFalse(self.spotify.is_authenticated("tests/auth_test_1.json"))
        self.assertFalse(self.spotify.is_authenticated("tests/test_auth_0.json"))
        self.assertTrue(self.spotify.is_authenticated("tests/test_auth_1.json"))

        return

    def test_authenticate(self) -> None:
        """Tests the `SpotifyAPI.authenticate` function."""
        self.spotify.authenticate("tests/auth_test_2.json")
        self.assertEqual(
            self.spotify.auth.keys(),
            {"access_token", "token_type", "expires_in", "authorize_after"},
        )
        self.assertEqual(self.spotify.auth.get("token_type"), "Bearer")

        return

    def test_search(self) -> None:
        """Tests the `SpotifyAPI.search` function."""
        if not self.spotify.is_authenticated("tests/auth_test_2.json"):
            self.spotify.authenticate("tests/auth_test_2.json")

        res = self.spotify.search("hasting", "fighting for you", market="US")
        self.assertEqual(res.keys(), {"tracks"})
        self.assertEqual(len(res.get("tracks").get("items")), 5)

        return

    def test_to_metadata(self) -> None:
        """Tests the `SpotifyAPI.to_metadata` function."""
        if not self.spotify.is_authenticated("tests/auth_test_2.json"):
            self.spotify.authenticate("tests/auth_test_2.json")

        self.spotify.search("hasting", "fighting for you", market="US")
        metadata = self.spotify.to_metadata()

        if metadata:
            self.assertEqual(metadata.title, "Fighting For You")
            self.assertEqual(metadata.artist, "Hasting")
            self.assertEqual(metadata.date, "2006-07-18")

            os.remove(f"{metadata.album_art}")

        return


if __name__ == "__main__":
    unittest.main()
