#!/bin/bash
_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $_dir/..
export BACKUPR_INTEGRATION_TESTS='false'
poetry run pytest
