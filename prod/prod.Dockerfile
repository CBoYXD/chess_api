FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/chess_api

RUN apt update && apt upgrade -y

COPY ./prod/prod_requirements.txt /usr/src/chess_api

RUN pip install --upgrade pip && \
    pip install -r /usr/src/chess_api/prod_requirements.txt

COPY . /usr/src/chess_api


CMD gunicorn --forwarded-allow-ips "*" \
    -k "uvicorn.workers.UvicornWorker" \
    -c "/usr/src/chess_api/prod/gunicorn_conf.py" \
    "src.api.app:app"
