#!/bin/bash

git pull
cd star_burger_dockered/prod
docker compose up -d
docker compose exec -it backend python manage.py collectstatic --noinput
docker compose exec -it backend python manage.py migrate
curl -H "X-Rollbar-Access-Token: $(cat star_burger/.env | grep ROLLBAR_TOKEN| cut -d "=" -f 2)" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "prod", "revision": "'"$(git rev-parse HEAD)"'", "rollbar_name": "gleb1112tiun", "local_username": "robinloksli", "status": "succeeded"}'
echo "Деплой успешно завершен"