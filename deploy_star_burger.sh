#!/bin/bash

set -e
cd /opt/Star-burger/star-burger
git pull
pip install -r requirements.txt
npm ci --dev
python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput
systemctl daemon-reload
curl -H "X-Rollbar-Access-Token: $(cat star_burger/.env | grep ROLLBAR_TOKEN| cut -d "=" -f 2)" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "prod", "revision": "'"$(git rev-parse HEAD)"'", "rollbar_name": "gleb1112tiun", "local_username": "robinloksli", "status": "succeeded"}'
echo "Деплой успешно завершен"
