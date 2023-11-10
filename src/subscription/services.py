import json
import random
from dataclasses import asdict
from datetime import date, datetime, timedelta

from tenacity import retry, stop_after_attempt, wait_fixed

from subscription.domain_models import (
    Card,
    Payment,
    PaymentMethod,
    PaymentMethodType,
    PaymentStatus,
    SubscriptionPlan,
    SubscriptionStatus,
    UserSubscription,
)
from subscription.serializers import CardSerializer
from subscription.unit_of_work import DjangoUnitOfWork


class SubscriptionService:
    def __init__(self, unit_of_work: DjangoUnitOfWork):
        self.uow = unit_of_work

    # FIXME: 테스트 목적으로 임시로 추가한 메서드
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _process_payment(self, user_id: int, amount: float):
        payment_method = PaymentMethod(
            method_type=PaymentMethodType.CREDIT_CARD,
            details={
                "card_number": "1234-5678-9012-3456",
                "expiry": "12/24",
                "cvc": "123",
            },
        )

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

        self.uow.payments.add(payment)

        return payment_success, payment

    def subscribe_user_to_plan(
        self, user_id: int, plan_name: str, payment_details: dict
    ):
        with self.uow:
            try:
                plan = self.uow.subscription_plans.get(plan_name)
            except ValueError as e:
                raise e

            today = date.today()
            user_subscription = UserSubscription(
                user_id=user_id,
                plan=plan,
                start_date=today,
                end_date=today + timedelta(days=plan.duration_days),
                status=SubscriptionStatus.ACTIVE,
            )
            self.uow.user_subscriptions.add(user_subscription)

            if payment_details["method_type"] == PaymentMethodType.CREDIT_CARD.value:
                card_serializer = CardSerializer(
                    data={
                        "card_number": payment_details["card_number"],
                        "card_expiry": payment_details["expiration_date"],
                        "card_cvc": payment_details["cvc"],
                    }
                )

                if card_serializer.is_valid(raise_exception=True):
                    details = card_serializer.data
            else:
                # NOTE: 다른 결제 수단이 추가되면 이곳에 추가
                details = "{}"

            payment_method = PaymentMethod(
                method_type=PaymentMethodType(payment_details["method_type"]),
                details=json.dumps(details),
            )
            self.uow.payment_methods.add(payment_method)

            payment = Payment(
                subscription=user_subscription,
                payment_method=payment_method,
                amount=plan.price,
                date=today,
                status=PaymentStatus.SUCCESS,
            )
            self.uow.payments.add(payment)

            return {
                "success": True,
                "message": f"User {user_id} has subscribed to {plan_name} plan successfully.",
            }

    def cancel_subscription(
        self,
        user_id: int,
    ):
        with self.uow:
            try:
                user_subscription = (
                    self.uow.user_subscriptions.get_active_subscription_by_user_id(
                        user_id
                    )
                )
            except ValueError as e:
                raise e

            user_subscription.status = SubscriptionStatus.CANCELED
            self.uow.user_subscriptions.update(user_subscription)
            return {
                "success": True,
                "message": f"User {user_id} has cancelled subscription successfully.",
            }

    def renew_subscription(self, user_id: int):
        with self.uow:
            current_subscription = (
                self.uow.user_subscriptions.get_active_subscription_by_user_id(user_id)
            )
            if (
                current_subscription
                and current_subscription.end_date > datetime.today().date()
            ):
                raise ValueError(
                    "Subscription has not expired yet and cannot be renewed."
                )

            payment_success, payment_details = self._process_payment(
                user_id, current_subscription.plan.price
            )
            if not payment_success:
                return {
                    "success": False,
                    "message": "Failed to process payment for subscription renewal.",
                }

            if current_subscription:
                current_subscription.status = SubscriptionStatus.EXPIRED
                self.uow.user_subscriptions.update(current_subscription)

            new_subscription = UserSubscription(
                user_id=user_id,
                plan=current_subscription.plan,
                start_date=datetime.today(),
                end_date=datetime.today()
                + timedelta(days=current_subscription.plan.duration_days),
                status=SubscriptionStatus.ACTIVE,
            )
            self.uow.user_subscriptions.add(new_subscription)

            # NOTE: 결제 정보 생성 및 추가하는 로직 (여기서는 생략)

            return {
                "success": True,
                "message": "Subscription renewed successfully.",
            }
