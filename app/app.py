"""
Based on: https://github.com/GoogleCloudPlatform/cloud-run-microservice-template-python/blob/main/app.py
"""

import os
import re
import signal
import sys
from types import FrameType

from flask import Flask, render_template, request, send_file
from yt_dlp import YoutubeDL


app = Flask(__name__)
AUTHENTICATION_PASSWORD = os.environ.get("AUTHENTICATION_PASSWORD")
# As per https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
video_mimetypes = {
    "3gp": "video/3gpp",
    "3g2": "video/3gpp2",
    "avi": "video/x-msvideo",
    "mpeg": "video/mpeg",
    "mp4": "video/mp4",
    "ogv": "video/ogg",
    "ts": "video/mp2t",
    "webm": "video/webm",
}


@app.before_request
def authenticate():
    password = request.args.get("pw")
    # Local runs do not need auth
    if AUTHENTICATION_PASSWORD and password != AUTHENTICATION_PASSWORD:
        return "Unauthorized", 401

@app.route("/", methods=["GET", "POST"])
def main() -> tuple:
    if request.method == "GET":
        return render_template("index.html")

    elif request.method == "POST":
        url = get_id_from_url(request.form["video_url"])
        if request.form["result_select"] == "video_small":
            return download_video(url)
        elif request.form["result_select"] == "gif_small":
            return download_gif(url)


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


def get_id_from_url(video_url: str) -> str:
    result = None
    if "/watch" in video_url:
        result = re.search(r"(?<=v=).+?(?=\b)", video_url)
    elif "/shorts" in video_url:
        result = re.search(r"(?<=/shorts/).+?(?=\b)", video_url)
    elif "youtu.be/" in video_url:
        result = re.search(r"(?<=youtu\.be/).+?(?=\b)", video_url)
    if result:
        return result[0]
    return f"Invalid URL: {video_url}", 400


def download_video(video_id: str):
    # Download video
    # The request below is equivalent to:
    #   yt-dlp -f "bestvideo*[ext=mp4][filesize<=20M]+bestaudio[ext=m4a][filesize<=4M] / bestvideo*[filesize<=19M]+bestaudio[filesize<=4M] / best[filesize<=25M] / worstvideo*+worstaudio* / worst" "https://www.youtube.com/watch?v={video_id}"
    # which will find the best video and audio combination that is preferably less than 25MB (with multiple fallbacks)
    url = f'https://www.youtube.com/watch?v={video_id}'
    parameters = {
        # "postprocessors": [{"key": "EmbedThumbnail"}],
        "format": "bestvideo*[ext=mp4][filesize<=20M]+bestaudio[ext=m4a][filesize<=4M] / bestvideo*[filesize<=19M]+bestaudio[filesize<=4M] / best[filesize<=25M] / worstvideo*+worstaudio* / worst",
        "outtmpl": "%(title|Untitled)s - %(uploader|Unknown)s [%(id)s].%(ext)s",
    }
    with YoutubeDL(params=parameters) as ydl:
        info = ydl.extract_info(url)

    # Locate downloaded file
    video = info['requested_downloads'][0]['filepath']
    print("file:", video)

    # Send file obj instead of sending path to overcome Cloud Run 32MB limit (https://cloud.google.com/run/quotas)
    # as_attachment indicates to the browser to download instead of displaying
    return send_file(
        open(video, 'rb'),
        as_attachment=True,
        mimetype=video_mimetypes.get(video.split('.')[-1], "video/mp4"),
        download_name=os.path.split(video)[1]
    )


def download_gif(video_id: str):
    # Download video
    # The request below is equivalent to:
    #   yt-dlp -f "bv[filesize<=512K] / wv" --ppa "VideoConvertor:-r 8 -an" --recode gif "https://www.youtube.com/watch?v={video_id}"
    # which will find the best video (no audio) under 512KB, or the worst video if that isn't available, and recode to gif at 8 fps, ignoring audio
    url = f'https://www.youtube.com/watch?v={video_id}'
    parameters = {
        "format": "bv[filesize<=512K] / wv",
        # "outtmpl": "%(title|Untitled)s - %(uploader|Unknown)s [%(id)s].%(ext)s",  # Causes issues with recoder
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "gif",
            # "when": "post_process"
        }],
        "postprocessor_args": {
            "VideoConvertor": "-r 8 -an",
        },
    }
    with YoutubeDL(params=parameters) as ydl:
        info = ydl.extract_info(url)

    # Locate downloaded file
    gif = info['requested_downloads'][0]['filepath']
    print("file:", gif)

    # Send file obj instead of sending path to overcome Cloud Run 32MB limit (https://cloud.google.com/run/quotas)
    # as_attachment indicates to the browser to download instead of displaying
    return send_file(
        open(gif, 'rb'),
        as_attachment=True,
        mimetype="image/gif",
        download_name=os.path.split(gif)[1]
    )


def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    # logger.info(f"Caught Signal {signal.strsignal(signal_int)}")

    # Safely exit program
    sys.exit(0)


if __name__ == "__main__":
    # Running application locally, outside of a Google Cloud Environment

    # Handles Ctrl-C termination
    signal.signal(signal.SIGINT, shutdown_handler)

    app.run(host="localhost", port=8080, debug=True)
