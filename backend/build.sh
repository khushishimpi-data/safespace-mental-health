#!/usr/bin/env bash
# Render build script for backend service
# Set in Render Dashboard → Build Command: chmod +x build.sh && ./build.sh
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
