from datetime import datetime, timedelta

from celery import shared_task
from celery.schedules import crontab

from subscription.domain import commands
from subscription.service_layer import message_bus, unit_of_work
from subscription_project.celery import app


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # NOTE: 매일 자정에 구독 갱신 태스크 실행
    sender.add_periodic_task(crontab(minute=0, hour=0), renew_expired_subscriptions.s())


@shared_task
def renew_expired_subscriptions():
    yesterday = (datetime.today() - timedelta(days=1)).date()
    with unit_of_work.DjangoUnitOfWork() as uow:
        expired_subscriptions = uow.user_subscriptions.get_subscriptions_expiring_on(
            yesterday
        )
        for subscription in expired_subscriptions:
            user_id = subscription.user_id
            message_bus.handle(commands.RenewSubscription(user_id=user_id), uow=uow)
