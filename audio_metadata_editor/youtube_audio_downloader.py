# @title YouTube video information and audio class { display-mode: "form" }
import os
from dataclasses import dataclass
from typing import Any, Optional

import ffmpeg
from pytube import YouTube


@dataclass
class YouTubeAudioDownloader:
    """Class for downloading audio from YouTube videos."""

    def _on_progress(self, *args: Any, **kwargs: Any) -> None:
        """Callback function to handle download progress updates."""
        return

    def _on_complete(self, *args: Any, **kwargs: Any) -> None:
        """Callback function to handle download completion."""
        return

    def get_audio(
        self, video_url: str, output_file: Optional[str] = None
    ) -> Optional[str]:
        """Download audio from a YouTube video.

        Parameters
        ----------
        video_url : str
            URL of the YouTube video.
        output_file : str, optional
            Output file path for the downloaded audio, by default None.

        Returns
        -------
        str or None
            Path to the downloaded audio file in M4A format, or None if download fails.
        """

        def convert_to_m4a(filename: str) -> str:
            """Convert a video file to M4A format.

            Parameters
            ----------
            filename : str
                Path to the input video file.

            Returns
            -------
            str
                Path to the output M4A audio file.
            """
            file_name, ext = os.path.splitext(filename)
            output_file = file_name + ".m4a"

            if os.path.exists(output_file):
                os.remove(output_file)

            ffmpeg.input(file_name + ext).output(output_file).run()
            os.remove(filename)

            return output_file

        self.video = YouTube(video_url, self._on_progress, self._on_complete)
        print(self.video.author, self.video.title)

        audio_streams = self.video.streams.filter(
            type="audio", mime_type="audio/mp4"
        ).order_by("abr")
        stream = audio_streams.last()

        # FEATURE: users can add custom download path/filename

        if stream:
            filename = os.path.basename(stream.download())

            return convert_to_m4a(filename)

        return
