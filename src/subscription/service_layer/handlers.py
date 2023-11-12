from subscription.adapters import email
from subscription.domain import events
from subscription.service_layer import unit_of_work


def send_payment_failed_notification(
    event: events.PaymentFailed,
    uow: unit_of_work.AbstractUnitOfWork,
):
    email.send(
        "test@made.com",
        f"failed {event.user_id} failure_reason: {event.failure_reason}",
    )
