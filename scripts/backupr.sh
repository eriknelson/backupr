#!/bin/bash
_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export BACKUPR_CONFIG_FILE=$_dir/../config/config.yaml
export BACKUPR_SECRETS_FILE=$_dir/../config/secrets.yaml
backupr run
