#!/usr/bin/env bash
set -o errexit  # stop immediately on any failure - never deploy a half-built app

pip install -r requirements.txt
python manage.py collectstatic --noinput
