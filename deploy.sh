#!/bin/bash

# See: https://cloud.google.com/sdk/gcloud/reference/run/deploy
gcloud run deploy youtube-util-p \
    --allow-unauthenticated \
    --cpu-throttling \
    --cpu 1 \
    --memory 4Gi \
    --source app
