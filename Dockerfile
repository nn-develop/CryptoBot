FROM python:3.13-slim-bookworm

WORKDIR .

COPY . .

RUN pip install --no-cache-dir -r requirements-dev.txt
