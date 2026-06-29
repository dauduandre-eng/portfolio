#!/usr/bin/env bash
set -o errexit  # stop immediately on any failure - never deploy a half-built app

pip install -r requirements.txt
python manage.py collectstatic --noinput
# Render's preDeployCommand field (the more correct place for this) isn't
# available on free-tier services - confirmed by Render's own Blueprint
# validator, not something documented up front. Running it here instead
# is the practical fallback: migrate is idempotent, so re-running it on
# every build when nothing's pending just no-ops instantly.
python manage.py migrate --noinput
