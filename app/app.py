import os
import signal
import subprocess
import sys
from types import FrameType

from flask import Flask, send_file
from yt_dlp import YoutubeDL


app = Flask(__name__)


@app.get("/")
def main() -> tuple:
    return "Hello, world!", 200


@app.get("/test")
def test():
    # Download video
    URLS = ['https://www.youtube.com/watch?v=BaW_jenozKc']
    with YoutubeDL() as ydl:
        ydl.download(URLS)
    # subprocess.run(["./youtube-dl", "https://www.youtube.com/watch?v=Rq83QosbjZ0"])

    # Locate downloaded file
    filenames = os.listdir(".")
    video = [filename for filename in filenames if filename.endswith(".mp4")]
    if not video:
        raise FileNotFoundError("An error has occurred")
    video = video[0]

    print("video:", video)
    return send_file(video)


def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    # logger.info(f"Caught Signal {signal.strsignal(signal_int)}")

    # Safely exit program
    sys.exit(0)


if __name__ == "__main__":
    # Running application locally, outside of a Google Cloud Environment

    # Handles Ctrl-C termination
    signal.signal(signal.SIGINT, shutdown_handler)

    app.run(host="localhost", port=8080, debug=True)
