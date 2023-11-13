import random
from datetime import date, datetime

from tenacity import retry, stop_after_attempt, wait_fixed

from subscription.domain.domain_models import (
    Payment,
    PaymentMethod,
    PaymentMethodType,
    PaymentStatus,
    SubscriptionPlan,
    UserSubscription,
)
from subscription.service_layer.unit_of_work import DjangoUnitOfWork


class SubscriptionService:
    def __init__(self, unit_of_work: DjangoUnitOfWork):
        self.uow = unit_of_work

    # FIXME: 테스트 목적으로 임시로 추가한 메서드
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def process_payment(self, user_id: int, amount: float):
        payment_method = PaymentMethod(
            method_type=PaymentMethodType.CREDIT_CARD,
            details={
                "card_number": "1234-5678-9012-3456",
                "expiry": "12/24",
                "cvc": "123",
            },
        )
        self.uow.payment_methods.add(payment_method)

        payment_success = random.choice([True, False])

        payment = Payment(
            subscription=self.uow.user_subscriptions.get_active_subscription_by_user_id(
                user_id
            ),
            payment_method=payment_method,
            amount=amount,
            date=datetime.now(),
            status=PaymentStatus.SUCCESS if payment_success else PaymentStatus.FAILED,
        )

        if not payment_success:
            payment.mark_failed("Random failure reason or specific error message")

        self.uow.payments.add(payment)

        return payment_success, payment

    def calculate_proration(
        self, current_subscription: UserSubscription, new_plan: SubscriptionPlan
    ):
        remaining_days = (current_subscription.end_date - date.today()).days

        # 일일 요금 계산
        daily_rate_current_plan = (
            current_subscription.plan.price / current_subscription.plan.duration_days
        )
        daily_rate_new_plan = new_plan.price / new_plan.duration_days

        # 비례 조정된 금액 계산
        prorated_amount = (
            daily_rate_new_plan - daily_rate_current_plan
        ) * remaining_days

        return prorated_amount, remaining_days
