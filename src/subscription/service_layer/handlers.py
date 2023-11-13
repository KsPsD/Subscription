import json
from datetime import date, datetime, timedelta

from subscription.adapters import email
from subscription.domain import commands, events
from subscription.domain.domain_models import (
    Payment,
    PaymentMethod,
    PaymentMethodType,
    PaymentStatus,
    SubscriptionPlan,
    SubscriptionStatus,
    UserSubscription,
)
from subscription.serializers import CardSerializer
from subscription.service_layer import unit_of_work
from subscription.service_layer.services import SubscriptionService


def send_payment_failed_notification(
    event: events.PaymentFailed,
    uow: unit_of_work.AbstractUnitOfWork,
):
    email.send(
        "test@made.com",
        f"failed {event.user_id} failure_reason: {event.failure_reason}",
    )


def subscribe_user_to_plan(
    command: commands.CreateSubscription,
    uow: unit_of_work.DjangoUnitOfWork,
):
    with uow:
        try:
            plan: SubscriptionPlan | None = uow.subscription_plans.get(
                command.plan_name
            )
        except ValueError as e:
            raise e

        user_subscription = plan.create_user_subscription(
            command.user_id, date.today(), plan.duration_days
        )
        uow.user_subscriptions.add(user_subscription)

        if (
            command.payment_details["method_type"]
            == PaymentMethodType.CREDIT_CARD.value
        ):
            card_serializer = CardSerializer(
                data={
                    "card_number": command.payment_details["card_number"],
                    "card_expiry": command.payment_details["expiration_date"],
                    "card_cvc": command.payment_details["cvc"],
                }
            )

            if card_serializer.is_valid(raise_exception=True):
                details = card_serializer.data
        else:
            # NOTE: 다른 결제 수단이 추가되면 이곳에 추가
            details = "{}"

        payment_method = PaymentMethod(
            method_type=PaymentMethodType(command.payment_details["method_type"]),
            details=json.dumps(details),
        )
        uow.payment_methods.add(payment_method)

        payment = Payment(
            subscription=user_subscription,
            payment_method=payment_method,
            amount=plan.price,
            date=date.today(),
            status=PaymentStatus.SUCCESS,
        )
        uow.payments.add(payment)

        return {
            "success": True,
            "message": f"User {command.user_id} has subscribed to {command.plan_name} plan successfully.",
        }


def cancel_subscription(
    command: commands.CancelSubscription,
    uow: unit_of_work.DjangoUnitOfWork,
):
    with uow:
        try:
            user_subscription = (
                uow.user_subscriptions.get_active_subscription_by_user_id(
                    command.user_id
                )
            )
        except ValueError as e:
            raise e

        user_subscription.status = SubscriptionStatus.CANCELED
        uow.user_subscriptions.update(user_subscription)
        return {
            "success": True,
            "message": f"User {command.user_id} has cancelled subscription successfully.",
        }


def renew_subscription(
    command: commands.RenewSubscription,
    uow: unit_of_work.DjangoUnitOfWork,
):
    with uow:
        current_subscription: UserSubscription = (
            uow.user_subscriptions.get_active_subscription_by_user_id(command.user_id)
        )
        current_subscription.renew()

        payment_success, payment_details = SubscriptionService(uow).process_payment(
            command.user_id, current_subscription.plan.price
        )
        if not payment_success:
            return {
                "success": False,
                "message": "Failed to process payment for subscription renewal.",
            }

        if current_subscription:
            current_subscription.status = SubscriptionStatus.EXPIRED
            uow.user_subscriptions.update(current_subscription)

        new_subscription = UserSubscription(
            user_id=command.user_id,
            plan=current_subscription.plan,
            start_date=datetime.today(),
            end_date=datetime.today()
            + timedelta(days=current_subscription.plan.duration_days),
            status=SubscriptionStatus.ACTIVE,
        )
        uow.user_subscriptions.add(new_subscription)

        return {
            "success": True,
            "message": "Subscription renewed successfully.",
        }


def change_subscription_plan(
    command: commands.ChangeSubscriptionPlan,
    uow: unit_of_work.DjangoUnitOfWork,
):
    with uow:
        try:
            current_subscription = (
                uow.user_subscriptions.get_active_subscription_by_user_id(
                    command.user_id
                )
            )
            new_plan = uow.subscription_plans.get(command.new_plan_name)

            prorated_amount, remaining_days = SubscriptionService(
                uow
            ).calculate_proration(current_subscription, new_plan)

            payment_success, payment_details = SubscriptionService(uow).process_payment(
                command.user_id, prorated_amount
            )
            if not payment_success:
                return {
                    "success": False,
                    "message": "Failed to process payment for plan change.",
                }

            current_subscription.end_date = date.today()
            current_subscription.status = SubscriptionStatus.CANCELED
            uow.user_subscriptions.update(current_subscription)

            new_subscription = UserSubscription(
                user_id=command.user_id,
                plan=new_plan,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=remaining_days),
                status=SubscriptionStatus.ACTIVE,
            )
            uow.user_subscriptions.add(new_subscription)

            return {
                "success": True,
                "message": "Subscription plan changed successfully.",
            }

        except ValueError as e:
            raise e
