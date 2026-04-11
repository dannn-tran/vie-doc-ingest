#!/bin/bash

BUCKET_PATH="vie-doc/**"

gcloud storage rm "gs://$BUCKET_PATH"