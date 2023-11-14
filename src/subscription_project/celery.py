from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subscription_project.settings")

app = Celery("subscription_project")

app.config_from_object("django.conf:settings", namespace="CELERY")

# 장고 앱 config에 있는 모든 celery 작업을 자동으로 로드합니다.
app.autodiscover_tasks()
