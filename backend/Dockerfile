# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /backend

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENV SECRET_KEY=django-insecure-0if40nf4nf93n4
ENV YANDEX_APIKEY=b9aee6c8-18ae-4374-b889-653fddb6b379

RUN python manage.py collectstatic --noinput
EXPOSE 8000
