import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional

from subscription import models


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


@dataclass
class UserSubscription:
    user_id: int
    plan_id: int
    start_date: date
    end_date: date
    status: SubscriptionStatus
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class PaymentMethod:
    method_type: PaymentMethodType
    details: dict
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Payment:
    subscription_id: int
    payment_method_id: int
    amount: float
    date: datetime
    status: PaymentStatus
    id: uuid.UUID = field(default_factory=uuid.uuid4)
