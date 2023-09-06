"""
Based on: https://github.com/GoogleCloudPlatform/cloud-run-microservice-template-python/blob/main/app.py
"""

import os
import signal
import sys
from types import FrameType

from flask import Flask, request, send_file
from yt_dlp import YoutubeDL
# from yt_dlp.postprocessor import EmbedThumbnailPP


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
    return "Hello, world!", 200


@app.get("/video")
def get_video() -> tuple:
    # print(request.args)
    video_id = request.args.get("id")
    if not video_id:
        return "Please specify `id`", 400
    return download_video(video_id)


@app.get("/gif")
def get_gif() -> tuple:
    video_id = request.args.get("id")
    if not video_id:
        return "Please specify `id`", 400
    return download_gif(video_id)


@app.get("/test")
def test():
    # Test video
    return download_video('BaW_jenozKc')

@app.get("/robots.txt")
def robots():
    """
    Disallow all robots.
    """
    return "User-agent: *\nDisallow: /", 200


def download_video(video_id: str):
    # Download video
    # The request below is equivalent to:
    #   yt-dlp -f "bestvideo*[ext=mp4][filesize<=20M]+bestaudio[ext=m4a][filesize<=4M] / bestvideo*[filesize<=19M]+bestaudio[filesize<=4M] / best[filesize<=25M] / best" "https://www.youtube.com/watch?v={video_id}"
    # which will find the best video and audio combination that is preferably less than 25MB (with multiple fallbacks)
    urls = [f'https://www.youtube.com/watch?v={video_id}']
    parameters = {
        # "postprocessors": [{"key": "EmbedThumbnail"}],
        "format": "bestvideo*[ext=mp4][filesize<=20M]+bestaudio[ext=m4a][filesize<=4M] / bestvideo*[filesize<=19M]+bestaudio[filesize<=4M] / best[filesize<=25M] / best"
    }
    with YoutubeDL(params=parameters) as ydl:
        ydl.download(urls)

    # Locate downloaded file
    filenames = os.listdir(".")
    video = [filename for filename in filenames if filename.endswith(".mp4")]
    if not video:
        raise FileNotFoundError("An error has occurred")
    video = video[0]
    print("video:", video)

    # TODO overcome Cloud Run 32MB limit: https://cloud.google.com/run/quotas
    # as_attachment indicates to the browser to download instead of displaying
    return send_file(video, as_attachment=True)


def download_gif(video_id: str):
    # Download video
    # The request below is equivalent to:
    #   yt-dlp -f "bv[filesize<=512K] / wv" --ppa "VideoConvertor:-r 8" --recode gif "https://www.youtube.com/watch?v={video_id}"
    # which will find the best video (no audio) under 512KB, or the worst video if that isn't available, and recode to gif at 8 fps, ignoring audio
    urls = [f'https://www.youtube.com/watch?v={video_id}']
    parameters = {
        "format": "bv[filesize<=512K] / wv",
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "gif"
        }],
        "postprocessor_args": {
            "VideoConvertor": "-r 8 -an",
        },
    }
    with YoutubeDL(params=parameters) as ydl:
        ydl.download(urls)

    # Locate downloaded file
    filenames = os.listdir(".")
    gif = [filename for filename in filenames if filename.endswith(".gif")]
    if not gif:
        raise FileNotFoundError("An error has occurred")
    gif = gif[0]
    print("video:", gif)

    # TODO overcome Cloud Run 32MB limit: https://cloud.google.com/run/quotas
    # as_attachment indicates to the browser to download instead of displaying
    return send_file(gif, as_attachment=True)


def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    # logger.info(f"Caught Signal {signal.strsignal(signal_int)}")

    # Safely exit program
    sys.exit(0)


if __name__ == "__main__":
    # Running application locally, outside of a Google Cloud Environment

    # Handles Ctrl-C termination
    signal.signal(signal.SIGINT, shutdown_handler)

    app.run(host="localhost", port=8080, debug=True)
