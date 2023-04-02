#!/bin/sh
#export SWIFTY_MODE='production'
#if [[ $SWIFTY_JOB != "" ]]; then
  #python -m "swifty.jobs.$SWIFTY_JOB"
#else
  ## Default runs the swifty server
  #GUNICORN_BIND_HOST=${GUNICORN_BIND_HOST:-'127.0.0.1'}
  #GUNICORN_BIND_PORT=${GUNICORN_BIND_PORT:-'5000'}
  #gunicorn -w 4 -b "$GUNICORN_BIND_HOST:$GUNICORN_BIND_PORT" 'swifty.app:create_app()'
#fi

echo "backupr entrypoint"
