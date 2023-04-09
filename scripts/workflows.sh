#!/bin/bash
_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
act -s B2_KEY_NAME="$B2_KEY_NAME" \
  -s B2_BUCKET_NAME="$B2_BUCKET_NAME" \
  -s B2_APPLICATION_KEY_ID="$B2_APPLICATION_KEY_ID" \
  -s B2_APPLICATION_KEY="$B2_APPLICATION_KEY"
