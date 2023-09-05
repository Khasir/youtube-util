import signal
import sys
from types import FrameType

from flask import Flask


app = Flask(__name__)


@app.route("/")
def main() -> tuple:
    return "Hello, world!", 200


def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    # logger.info(f"Caught Signal {signal.strsignal(signal_int)}")

    # Safely exit program
    sys.exit(0)


if __name__ == "__main__":
    # Running application locally, outside of a Google Cloud Environment

    # handles Ctrl-C termination
    signal.signal(signal.SIGINT, shutdown_handler)

    app.run(host="localhost", port=8080, debug=True)
