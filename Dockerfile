FROM python:3.11-slim

WORKDIR /usr/src/chess_api

COPY ./requirements.txt /usr/src/chess_api

RUN pip install --upgrade pip && \
    pip install -r /usr/src/chess_api/requirements.txt

COPY . /usr/src/chess_api

CMD uvicorn src.api.app:app --host ${API_HOST} --port ${API_PORT} --reload
