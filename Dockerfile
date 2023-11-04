# Pull base image
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
