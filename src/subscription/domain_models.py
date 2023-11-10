import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import Enum


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


@dataclass
class SubscriptionPlan:
    name: PlanName
    price: float
    payment_cycle: PaymentCycle
    description: str
    duration_days: int
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


@dataclass
class UserSubscription:
    user_id: int
    plan: SubscriptionPlan
    start_date: date
    end_date: date
    status: SubscriptionStatus
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


@dataclass
class PaymentMethod:
    method_type: PaymentMethodType
    details: dict
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


@dataclass
class Payment:
    subscription: UserSubscription
    payment_method: PaymentMethod
    amount: float
    date: datetime
    status: PaymentStatus
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


@dataclass
class Card:
    card_number: str
    card_expiry: str
    card_cvc: str
