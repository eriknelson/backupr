#!/bin/bash
_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $_dir/..
poetry run pylint backupr tests scripts/ci/deep_int_test.py
