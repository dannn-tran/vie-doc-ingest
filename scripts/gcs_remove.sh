#!/bin/bash

KEY_FILE="../.gc-secrets/key.json"
BUCKET_PATH="vie-doc/**"

gcloud auth activate-service-account --key-file="$KEY_FILE"
gcloud storage rm "gs://$BUCKET_PATH"