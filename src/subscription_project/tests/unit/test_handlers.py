import random
from datetime import date
from unittest import mock

from django.test import TestCase

from subscription.domain import commands
from subscription.domain.domain_models import (
    PaymentMethodType,
    SubscriptionPlan,
    SubscriptionStatus,
    UserSubscription,
)
from subscription.service_layer import message_bus
from subscription.service_layer.services import SubscriptionService
from subscription_project.tests.unit.fake import FakeUnitOfWork


class TestCreateSubscription(TestCase):
    def setUp(self):
        self.user_id = 1
        self.plan_name = "Basic"
        self.payment_details = {
            "method_type": PaymentMethodType.CREDIT_CARD.value,
            "card_number": "4242-4242-4242-4242",
            "expiration_date": "12/25",
            "cvc": "123",
        }
        self.plan = SubscriptionPlan(
            name=self.plan_name,
            price=10.00,
            payment_cycle="monthly",
            description="Basic Plan",
            duration_days=30,
        )
        self.uow = FakeUnitOfWork()
        self.service = SubscriptionService(self.uow)

    def test_subscribe_user_to_plan_success(self):
        self.uow.subscription_plans.add(
            SubscriptionPlan(
                name=self.plan_name,
                price=10.00,
                payment_cycle="monthly",
                description="Basic Plan",
                duration_days=30,
            )
        )
        results = message_bus.handle(
            commands.CreateSubscription(
                self.user_id,
                self.plan_name,
                self.payment_details,
            ),
            self.uow,
        )
        response = results.pop()
        self.assertTrue(response["success"])
        self.assertIn("has subscribed to Basic plan successfully", response["message"])
        self.assertTrue(self.uow.committed)

    def test_subscribe_user_to_plan_with_invalid_plan(self):
        with self.assertRaises(ValueError) as context:
            results = message_bus.handle(
                commands.CreateSubscription(
                    self.user_id,
                    self.plan_name,
                    self.payment_details,
                ),
                self.uow,
            )

            self.assertIsInstance(context, ValueError)

            self.assertFalse(self.uow.committed)
            self.assertTrue(self.uow.rolled_back)

    def test_cancel_subscription_success(self):
        self.uow.subscription_plans.add(
            SubscriptionPlan(
                name=self.plan_name,
                price=10.00,
                payment_cycle="monthly",
                description="Basic Plan",
                duration_days=30,
            )
        )
        message_bus.handle(
            commands.CreateSubscription(
                self.user_id,
                self.plan_name,
                self.payment_details,
            ),
            self.uow,
        )

        results = message_bus.handle(
            commands.CancelSubscription(
                self.user_id,
            ),
            self.uow,
        )

        response = results.pop()

        self.assertTrue(response["success"])
        self.assertEqual(
            f"User {self.user_id} has cancelled subscription successfully.",
            response["message"],
        )
        self.assertTrue(self.uow.committed)

    def test_cancel_subscription_with_invalid_user(self):
        with self.assertRaises(ValueError) as context:
            results = message_bus.handle(
                commands.CancelSubscription(
                    self.user_id,
                ),
                self.uow,
            )

            self.assertIsInstance(context, ValueError)

            self.assertFalse(self.uow.committed)
            self.assertTrue(self.uow.rolled_back)

    def test_renew_subscription_success(self):
        self.uow.subscription_plans.add(self.plan)
        self.uow.user_subscriptions.add(
            UserSubscription(
                user_id=self.user_id,
                plan=self.plan,
                start_date=date.today(),
                end_date=date.today(),
                status=SubscriptionStatus.ACTIVE,
            )
        )

        with mock.patch.object(
            self.service, "process_payment", return_value=(True, {})
        ) as mock_method:
            results = message_bus.handle(
                commands.RenewSubscription(
                    self.user_id,
                ),
                self.uow,
            )
            response = results.pop()

            self.assertTrue(response["success"])
            self.assertTrue(self.uow.committed)

    def test_change_subscription_plan_with_success(self):
        self.uow.subscription_plans.add(self.plan)
        self.uow.subscription_plans.add(
            SubscriptionPlan(
                name="Premium",
                price=20.00,
                payment_cycle="monthly",
                description="Premium Plan",
                duration_days=30,
            )
        )
        self.uow.user_subscriptions.add(
            UserSubscription(
                user_id=self.user_id,
                plan=self.plan,
                start_date=date.today(),
                end_date=date.today(),
                status=SubscriptionStatus.ACTIVE,
            )
        )

        with mock.patch.object(random, "choice", return_value=True) as mock_method:
            results = message_bus.handle(
                commands.ChangeSubscriptionPlan(
                    self.user_id,
                    "Premium",
                ),
                self.uow,
            )
            response = results.pop()

            self.assertTrue(response["success"])
            self.assertTrue(self.uow.committed)

    def test_change_subscription_plan_with_failure(self):
        self.uow.subscription_plans.add(self.plan)
        self.uow.subscription_plans.add(
            SubscriptionPlan(
                name="Premium",
                price=20.00,
                payment_cycle="monthly",
                description="Premium Plan",
                duration_days=30,
            )
        )
        self.uow.user_subscriptions.add(
            UserSubscription(
                user_id=self.user_id,
                plan=self.plan,
                start_date=date.today(),
                end_date=date.today(),
                status=SubscriptionStatus.ACTIVE,
            )
        )

        with mock.patch.object(random, "choice", return_value=False) as mock_method:
            results = message_bus.handle(
                commands.ChangeSubscriptionPlan(
                    self.user_id,
                    "Premium",
                ),
                self.uow,
            )
            response = results.pop()

            self.assertFalse(response["success"])
            self.assertEqual(
                response["message"], "Failed to process payment for plan change."
            )
