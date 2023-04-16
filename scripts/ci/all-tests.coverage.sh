#!/bin/bash
_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
projectRoot="$_dir/../.."
if [[ -z "$B2_KEY_NAME" ]]; then
  echo "B2_KEY_NAME env var missing!"
  echo "ERROR: Missing secret"
  exit 1
fi
if [[ -z "$B2_BUCKET_NAME" ]]; then
  echo "B2_BUCKET_NAME env var missing!"
  echo "ERROR: Missing secret"
  exit 1
fi
if [[ -z "$B2_APPLICATION_KEY_ID" ]]; then
  echo "B2_APPLICATION_KEY_ID env var missing!"
  echo "ERROR: Missing secret"
  exit 1
fi
if [[ -z "$B2_APPLICATION_KEY" ]]; then
  echo "B2_APPLICATION_KEY env var missing!"
  echo "ERROR: Missing secret"
  exit 1
fi

export BACKUPR_INTEGRATION_TESTS='true'
export B2_BUCKET_NAME="$B2_BUCKET_NAME"
export B2_KEY_NAME="$B2_KEY_NAME"
export B2_APPLICATION_KEY_ID="$B2_APPLICATION_KEY_ID"
export B2_APPLICATION_KEY="$B2_APPLICATION_KEY"

pushd $projectRoot
if [[ -n "$TEST_OUTPUT" ]]; then
  poetry run pytest -s --cov-report=xml --cov=backupr tests/
else
  poetry run pytest --cov-report=xml --cov=backupr tests/
fi
popd