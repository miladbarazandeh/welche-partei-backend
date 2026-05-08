FROM python:3.13-slim AS BASE

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /app
WORKDIR /app

RUN pip install --upgrade pip 

COPY ./requirements.txt ./

RUN apt-get update && \
  apt-get install -y \
  gcc \
  libpq-dev && \
  pip install --no-cache-dir -r requirements.txt && \
  apt-get remove -y gcc && \
  rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "backend.wsgi:application"]