PIPENV_RUN = pipenv run
BASE_DIR = ./src
MANAGE_PY = $(BASE_DIR)/manage.py
DOCKER_COMPOSE = docker-compose 
APP_NAME = subscription

.PHONY: test clean migrate migrations run createsuperuser install-deps docker-build docker-up docker-down test-coverage

migrations:
	$(PIPENV_RUN) python $(MANAGE_PY) makemigrations

migrate:
	$(PIPENV_RUN) python $(MANAGE_PY) migrate $(APP_NAME) $(target)

showmigrations:
	$(PIPENV_RUN) python $(MANAGE_PY) showmigrations

test:
	cd $(BASE_DIR) && $(PIPENV_RUN) python manage.py test $(target)

test-coverage:
	cd $(BASE_DIR) && $(PIPENV_RUN) coverage run --source='.' manage.py test $(target)
	cd $(BASE_DIR) && $(PIPENV_RUN) coverage xml

install-deps:
	$(PIPENV_RUN) pipenv install --dev --deploy --ignore-pipfile

clean:
	$(PIPENV_RUN) python $(MANAGE_PY) flush --no-input
	rm -rf .cache
run:
	$(PIPENV_RUN) python $(MANAGE_PY) runserver

create_superuser:
	@echo "Creating superuser..."
	$(PIPENV_RUN) python $(MANAGE_PY) shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'password') if not User.objects.filter(username='admin').exists() else print('Superuser already exists.')"

show_urls:
	$(PIPENV_RUN) python $(MANAGE_PY) show_urls

# Docker
docker-build:
	$(DOCKER_COMPOSE) build

docker-up:
	$(DOCKER_COMPOSE) up $(option)

docker-down:
	$(DOCKER_COMPOSE) down