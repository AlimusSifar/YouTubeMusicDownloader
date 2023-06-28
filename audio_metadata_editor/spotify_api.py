# @title Spotify authentication { display-mode: "form" }
import base64
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from io import BytesIO
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup
from PIL import Image
from requests import Response

from .metadata import Metadata


@dataclass
class SpotifyAPI:
    """Class representing the Spotify API."""

    auth: dict[str, Any] = field(default_factory=lambda: {})

    def is_authenticated(self, filename: str = "auth.json") -> bool:
        """Check if the user is authenticated.

        Parameters
        ----------
        filename : str, optional
            The name of the authentication file, by default "auth.json"

        Returns
        -------
        bool
            True if authenticated, False otherwise.
        """
        if not os.path.exists(filename):
            # create a auth.json file and return false
            with open(filename, "w") as jsonfile:
                json.dump(self.auth, jsonfile)
            return False

        with open(filename, "rb") as jsonfile:
            # check if the auth has expired
            self.auth = json.load(jsonfile)
            if (
                not self.auth
                or datetime.now().timestamp() > self.auth["authorize_after"]
            ):
                return False

        return True

    def authenticate(self, filename: str = "auth.json") -> None:
        """Authenticate the user.

        Parameters
        ----------
        filename : str, optional
            The name of the authentication file, by default "auth.json"
        """
        now = datetime.now().timestamp()

        # Spotify - App Tester - App Token
        B64ClientID = base64.standard_b64encode(b"91a704941f39447980874befd4221bb6:")
        B64AuthToken = (
            f"{B64ClientID.decode()}MmEwYjBjMDY3MTZkNDg0MWIxNTc2NmI3YWI4MzE5Njk="
        )

        ENDPOINT = "https://accounts.spotify.com/api/token"
        form = {"grant_type": "client_credentials"}
        headers = {
            "Authorization": f"Basic {B64AuthToken}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        self.auth = requests.post(ENDPOINT, params=form, headers=headers).json()
        self.auth["authorize_after"] = now + self.auth["expires_in"]

        with open(filename, "w") as jsonfile:
            json.dump(self.auth, jsonfile, indent=2)
        return

    def search(
        self,
        *query: str,
        type_: str = "track",  # REQUIRED: Values: "album", "artist", "playlist", "track", "show", "episode", "audiobook"
        market: Optional[str] = None,
        limit: int = 5,  # Value Range: 0 - 50
        offset: int = 0,  # Value Range: 0 - 1000
        include_external: Optional[str] = None,  # Values: "audio"
    ) -> Any:
        """Search for tracks, albums, artists, playlists, shows, episodes, or audiobooks on Spotify.

        Parameters
        ----------
        query : str
            The search query.
        type_ : str, optional
            The type of item to search for, by default "track".
        market : str, optional
            An ISO 3166-1 alpha-2 country code to limit the search results, by default None.
        limit : int, optional
            The maximum number of items to return, by default 5.
        offset : int, optional
            The index of the first item to return, by default 0.
        include_external : str, optional
            Whether to include external audio content in the search results, by default None.

        Returns
        -------
        Any
            The search results.
        """
        ENDPOINT = "https://api.spotify.com/v1/search"
        params = {
            # "q": f"{video.title}, {video.author}",  # REQUIRED
            "q": ", ".join(map(str, query)),  # REQUIRED
            "type": type_,  # REQUIRED: Values: "album", "artist", "playlist", "track", "show", "episode", "audiobook"
            "market": market,
            "limit": limit,  # Value Range: 0 - 50
            "offset": offset,  # Value Range: 0 - 1000
            "include_external": include_external,  # Values: "audio"
        }
        headers = {
            "Authorization": f"{self.auth.get('token_type')} {self.auth.get('access_token')}",
            "Content-Type": "application/json",
        }

        self.res = requests.get(ENDPOINT, params=params, headers=headers).json()
        return self.res

    def to_metadata(self) -> Optional[Metadata]:
        """Convert the Spotify API response to metadata.

        Returns
        -------
        Metadata, optional
            The converted metadata or None if no tracks found.
        """

        def request(url: str, params=None) -> Response:
            """Send a GET request to the specified URL.

            Parameters
            ----------
            url : str
                The URL to send the request to.
            params : dict, optional
                The query parameters for the request, by default None.

            Returns
            -------
            Response
                The response object.
            """
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
                )
                # "User-Agent": "Mozilla/5.0",
            }

            return requests.get(url, params, headers=headers)

        def music_search(*args: str) -> Optional[str]:
            """Perform a music search using Google search.

            Parameters
            ----------
            args : str
                The search query.

            Returns
            -------
            str, optional
                The URL of the music search result or None if not found.
            """
            # make a request to website
            query = ", ".join(map(str, args))
            params = {"q": f"site:music.apple.com {query} "}
            res = request("https://google.com/search", params)
            soup = BeautifulSoup(res.content, "html.parser")

            # Find the div with id 'rso' within the specified hierarchy
            div_rso = soup.select_one(
                "body > div#main > div#cnt > div#rcnt > div#center_col > div#res > div#search > div > div#rso"
            )

            # Find all anchor tags (a) within the 'div_rso' that match the regex pattern
            if div_rso:
                # Create a regular expression pattern
                pattern = re.compile(r"^https://music.apple.com/[a-z]{2}/album/\S+/\d+")
                return sorted([a["href"] for a in div_rso.find_all("a", href=pattern)])[
                    -1
                ]
            return

        def scrape_data(url: str) -> dict[str, Any]:
            """Scrape data from a specified URL.

            Parameters
            ----------
            url : str
                The URL to scrape data from.

            Returns
            -------
            dict[str, Any]
                The scraped data.
            """
            data = {}
            # make a request to website
            res = request(url)
            soup = BeautifulSoup(res.content, "html.parser")
            div_heading = soup.select_one(
                (
                    "div#scrollable-page > main > div.content-container > div.section > div.section-content > "
                    "div.container-detail-header > div.headings > div.headings__metadata-bottom"
                )
            )
            div_footer = soup.select_one(
                (
                    "div#scrollable-page > main > div.content-container > div.section > div.section-content > "
                    "div.tracklist-footer > div.footer-body > p.description"
                )
            )

            if div_heading:
                data["genre"] = div_heading.text.split(" · ")[0].title()
            if div_footer:
                data["copyright"] = div_footer.text.split("\n")[-1].strip()

            return data

        def get_artists(artists: Any) -> str:
            """Get the names of the artists.

            Parameters
            ----------
            artists : Any
                The artist data.

            Returns
            -------
            str
                The names of the artists.
            """
            artists = [artist.get("name") for artist in artists]
            if len(artists) > 1:
                artists_ = ", ".join(artists[:-1])
                artists_ = f"{artists_} & {artists[-1]}"
                return artists_
            return artists.pop()

        def get_album_art(album_arts: list[dict[str, Any]], filename: str) -> str:
            """Get the album art.

            Parameters
            ----------
            album_arts : list[dict[str, Any]]
                The album art data.
            filename : str
                The filename to save the album art.

            Returns
            -------
            str
                The filename of the saved album art.
            """
            # IMPROVEMENT: instead of saving the image, store it as bytes and return
            # then use the bytes directly to set the album_art
            res = requests.get(str(album_arts[0].get("url")))
            Image.open(BytesIO(res.content)).save(f"{filename}.jpg")
            return f"{filename}.jpg"

        if not self.res.get("tracks"):
            return

        items = self.res.get("tracks").get("items")
        item_1 = items[0]

        filename: str = item_1.get("album").get("id")

        title: str = item_1.get("name")
        album_name: str = item_1.get("album").get("name")
        album_type: str = item_1.get("album").get("album_type")
        album_artist: str = get_artists(item_1.get("album").get("artists"))

        if album_type == "single":
            album: str = f"{album_name} - {album_type.title()}"
        elif album_type == "ep":
            album: str = f"{album_name} - {album_type.upper()}"
        else:
            album: str = album_name

        data: Optional[Any] = music_search(album_artist, album_name)
        if data:
            data = scrape_data(data)

        artist: str = get_artists(item_1.get("artists"))
        track: int = item_1.get("track_number")
        total_tracks: int = item_1.get("album").get("total_tracks")
        date: str = item_1.get("album").get("release_date")
        genre: Optional[str] = data.get("genre") if data else None
        composer: Optional[str] = None  # TODO: NOT IMPLEMENTED
        disk: int = item_1.get("disc_number")
        compilation: Optional[int] = 1 if album_type == "compilation" else None
        gapless_playback = None
        rating = int(item_1.get("explicit"))
        # media_type = ...
        copyright: Optional[str] = data.get("copyright") if data else None
        account_id = "alimussifar@icloud.com"
        purchase_date: Optional[str] = None  # TODO: NOT IMPLEMENTED
        # sort_name = ...
        # sort_album = ...
        # sort_album_artist = ...
        # sort_artist = ...
        # sort_composer = ...
        lyrics: Optional[str] = None  # TODO: NOT IMPLEMENTED
        album_art: str = get_album_art(item_1.get("album").get("images"), filename)
        comment = (
            "Metadata collected from SpotifyAPI and added via the "
            "python package named 'Mutagen'"
        )

        return Metadata(
            title=title,
            album=album,
            album_artist=album_artist,
            artist=artist,
            track=(track, total_tracks),
            date=date,
            genre=genre,
            composer=composer,
            disk=(disk, disk),
            compilation=compilation,
            gapless_playback=gapless_playback,
            rating=rating,
            media_type=1,
            copyright=copyright,
            account_id=account_id,
            purchase_date=purchase_date,
            sort_name=title,
            sort_album=album,
            sort_album_artist=album_artist,
            sort_artist=artist,
            sort_composer=composer,
            lyrics=lyrics,
            album_art=album_art,
            comment=comment,
        )
