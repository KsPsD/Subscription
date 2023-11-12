import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import Enum

from subscription.domain.events import PaymentFailed


class PlanName(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


class PaymentCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    ONCE = "once"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"
    CANCELED = "canceled"


class PaymentMethodType(str, Enum):
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    POINT = "point"


class PaymentStatus(str, Enum):
    SUCCESS = "Succeeded"
    PENDING = "pending"
    FAILED = "failed"
    PROCESSING = "processing"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class SubscriptionPlan:
    def __init__(
        self,
        name: PlanName,
        price: float,
        payment_cycle: PaymentCycle,
        description: str,
        duration_days: int,
        id: uuid.UUID = None,
    ):
        self.name = name
        self.price = price
        self.payment_cycle = payment_cycle
        self.description = description
        self.duration_days = duration_days
        self.id = id or uuid.uuid4()
        self.events = []

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class UserSubscription:
    def __init__(
        self,
        user_id: int,
        plan: SubscriptionPlan,
        start_date: date,
        end_date: date,
        status: SubscriptionStatus,
        id: uuid.UUID = None,
    ):
        self.user_id = user_id
        self.plan = plan
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.id = id or uuid.uuid4()
        self.events = []

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class PaymentMethod:
    def __init__(self, method_type: PaymentMethodType, details: dict, id=None):
        self.method_type = method_type
        self.details = details
        self.id = id or uuid.uuid4()
        self.events = []

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class Payment:
    def __init__(
        self,
        subscription: UserSubscription,
        payment_method: PaymentMethod,
        amount: float,
        date: datetime,
        status: PaymentStatus,
        id=None,
    ):
        self.subscription = subscription
        self.payment_method = payment_method
        self.amount = amount
        self.date = date
        self.status = status
        self.id = id or uuid.uuid4()
        self.events = []

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def mark_failed(self, failure_reason: str):
        self.status = PaymentStatus.FAILED
        failed_event = PaymentFailed(
            payment_id=str(self.id),
            user_id=self.subscription.user_id,
            amount=self.amount,
            failure_reason=failure_reason,
        )
        self.events.append(failed_event)


@dataclass(frozen=True)
class Card:
    card_number: str
    card_expiry: str
    card_cvc: str
