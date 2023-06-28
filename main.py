from audio_metadata_editor import SpotifyAPI, YouTubeAudioDownloader

VIDEO_URL: str = "https://www.youtube.com/watch?v=eHZ-Qg7vZvc"
ADD_MUSIC_METADATA: bool = True
# ADD_MUSIC_METADATA: bool = False


def main() -> None:
    print("[INFO] Getting YouTube data to download.")
    ytad = YouTubeAudioDownloader()
    audio_path = ytad.get_audio(VIDEO_URL)
    print(f"[INFO] Found audio: `{audio_path}`")

    if not ADD_MUSIC_METADATA:
        print("[INFO] Metadata skipped.")
    else:
        print("[INFO] Collecting metadata, please wait.")

        spotify = SpotifyAPI()
        if not spotify.is_authenticated():
            spotify.authenticate()

        print("[INFO] Found audio metadata from SpotifyAPI.")
        y = spotify.search(
            ytad.video.author,
            ytad.video.title,
            # market="US",
            limit=1,
        )
        # print(y)
        print("[INFO] Adding metadata to audio.")
        metadata = spotify.to_metadata()
        if metadata and audio_path:
            print(metadata)
            metadata.add_to_m4a(audio_path, autosave=True)

    print("[INFO] Program ended.")


if __name__ == "__main__":
    main()
