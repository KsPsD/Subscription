from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Optional


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


@dataclass
class UserSubscription:
    user_id: int
    plan_id: int
    start_date: date
    end_date: date
    status: SubscriptionStatus


@dataclass
class PaymentMethod:
    user_id: int
    method_type: PaymentMethodType
    details: dict


@dataclass
class Payment:
    subscription: UserSubscription
    payment_method: Optional[PaymentMethod]
    amount: float
    date: datetime
    status: PaymentStatus
