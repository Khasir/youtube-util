import os
import signal
import sys
from types import FrameType

from flask import Flask, request, send_file
from yt_dlp import YoutubeDL


app = Flask(__name__)
AUTHENTICATION_PASSWORD = os.environ.get("AUTHENTICATION_PASSWORD")


@app.before_request
def authenticate():
    password = request.args.get("pw")
    # Local runs do not need auth
    if AUTHENTICATION_PASSWORD and password != AUTHENTICATION_PASSWORD:
        return "Unauthorized", 401


@app.get("/")
def main() -> tuple:
    # print(request.args)
    video_id = request.args.get("id")
    if not video_id:
        return "Please specify `id`", 400
    return download(video_id)

    # return "Hello, world!", 200


@app.get("/test")
def test():
    return download('BaW_jenozKc')


def download(video_id: str):
    # Download video
    URLS = [f'https://www.youtube.com/watch?v={video_id}']
    with YoutubeDL() as ydl:
        ydl.download(URLS)

    # Locate downloaded file
    filenames = os.listdir(".")
    video = [filename for filename in filenames if filename.endswith(".mp4")]
    if not video:
        raise FileNotFoundError("An error has occurred")
    video = video[0]

    print("video:", video)
    return send_file(video, as_attachment=True)


def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    # logger.info(f"Caught Signal {signal.strsignal(signal_int)}")

    # Safely exit program
    sys.exit(0)


if __name__ == "__main__":
    # Running application locally, outside of a Google Cloud Environment

    # Handles Ctrl-C termination
    signal.signal(signal.SIGINT, shutdown_handler)

    app.run(host="localhost", port=8080, debug=True)
