#!/bin/bash
APP_DIR="/root/Markdown-Blog"
VENV_DIR="$APP_DIR/venv"
SCREEN_NAME="blog"
PYTHON_SCRIPT="main"

cd "$APP_DIR"
screen -dmS "$SCREEN_NAME" "$VENV_DIR"/bin/uvicorn "$PYTHON_SCRIPT":app --host 0.0.0.0 --port 443 --ssl-keyfile=/etc/letsencrypt/live/seza.si/privkey.pem --ssl-certfile=/etc/letsencrypt/live/seza.si/fullchain.pem