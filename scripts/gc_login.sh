#!/bin/bash

PROJECT_ID="vie-ocr"

gcloud auth application-default login
gcloud auth application-default set-quota-project "$PROJECT_ID"