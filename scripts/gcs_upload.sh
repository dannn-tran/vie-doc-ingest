#!/bin/bash

BUCKET_NAME="vie-doc"
LOCAL_DIR="../thanh-nghi/images"
REMOTE_PREFIX="thanh-nghi/images"

# 1. Path Normalization (SRC: with trailing slash; DEST: no trailing slash)
SRC="${LOCAL_DIR%/}/"
DEST="gs://${BUCKET_NAME}/${REMOTE_PREFIX%/}"

# 2. Pre-flight Check
if [[ ! -d "$LOCAL_DIR" ]]; then
    echo "❌ Error: Local directory '$LOCAL_DIR' does not exist."
    exit 1
fi

echo "🚀 Starting upload..."
echo "Source:      $SRC"
echo "Destination: $DEST"

# 3. Execution
if gcloud storage rsync "$SRC" "$DEST" -r -x ".*\.DS_Store$"; then
    echo "✅ Upload complete!"
else
    echo "❌ Upload failed. Ensure the Service Account has 'Storage Object Admin' roles."
    exit 1
fi