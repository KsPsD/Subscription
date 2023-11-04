from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class PlanName(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


@dataclass
class SubscriptionPlan:
    name: PlanName
    price: float
    description: str
    duration_days: int


@dataclass
class UserSubscription:
    user_id: int
    plan: SubscriptionPlan
    start_date: date
    end_date: date
    active: bool


@dataclass
class PaymentMethod:
    user_id: int
    method_type: str
    details: dict


@dataclass
class Payment:
    subscription: UserSubscription
    payment_method: Optional[PaymentMethod]
    amount: float
    date: date
    successful: bool
