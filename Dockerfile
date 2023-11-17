# 단계 1: Node.js를 사용하여 Tailwind CSS 빌드
FROM node:latest as tailwindbuild

WORKDIR /app

COPY tailwind.config.js /app/
COPY src/subscription/static/styles.css /app/src/subscription/static/

RUN npm install -g tailwindcss postcss autoprefixer
RUN tailwindcss -i /app/src/subscription/static/styles.css -o /app/src/subscription/static/output.css

# 단계 2: Python 환경 설정 및 애플리케이션 실행
FROM python:3.11.5

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_ENV "proudction"

WORKDIR /app

# Install python dependencies
RUN pip install pipenv
COPY ./Pipfile ./Pipfile.lock /app/
RUN pipenv install --system --dev
COPY ./entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh


COPY ./Makefile /app/
COPY ./src /app/src


EXPOSE 8000
ENV PYTHONPATH=/app/src

ENTRYPOINT ["/app/entrypoint.sh"]
