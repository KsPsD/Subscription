PIPENV_RUN = pipenv run
BASE_DIR = ./src
MANAGE_PY = $(BASE_DIR)/manage.py

.PHONY: test clean migrate migrations run createsuperuser

migrations:
	$(PIPENV_RUN) python $(MANAGE_PY) makemigrations

migrate:
	$(PIPENV_RUN) python $(MANAGE_PY) migrate

test:
	cd $(BASE_DIR) && $(PIPENV_RUN) python manage.py test $(target)

clean:
	$(PIPENV_RUN) python $(MANAGE_PY) flush --no-input
	rm -rf .cache
run:
	$(PIPENV_RUN) python $(MANAGE_PY) runserver

create_superuser:
	@echo "Creating superuser..."
	$(PIPENV_RUN) python $(MANAGE_PY) shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'password') if not User.objects.filter(username='admin').exists() else print('Superuser already exists.')"


