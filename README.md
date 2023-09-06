# youtube-util
Endpoint utility for downloading YouTube videos.

## First-time setup
Make sure you're running Python 3!

```sh
mkdir env
cd env
python -m venv .
source bin/activate
cd ..
pip install --upgrade wheel pip
pip install -r app/requirements.txt
```

Install gcloud [todo fill out]

Install [ffmpeg](https://ffmpeg.org/):
```sh
# assuming Mac
brew install ffmpeg
```
## Local testing
```sh
cd app
python -m app
```

## Deployment
```sh
./deploy.sh
```
