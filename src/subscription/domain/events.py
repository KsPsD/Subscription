class Event:
    pass


class PaymentFailed(Event):
    def __init__(
        self, payment_id: str, user_id: int, amount: float, failure_reason: str
    ):
        self.payment_id = payment_id
        self.user_id = user_id
        self.amount = amount
        self.failure_reason = failure_reason

    def __str__(self):
        return f"PaymentFailedEvent(payment_id={self.payment_id}, user_id={self.user_id}, amount={self.amount}, failure_reason={self.failure_reason})"
