from unittest import mock

from django.test import TestCase

from subscription.domain_models import PaymentMethodType, SubscriptionPlan
from subscription.services import SubscriptionService
from subscription.unit_of_work import DjangoUnitOfWork
from subscription_project.tests.unit.fake import FakeUnitOfWork


class SubscribeUserToPlanTestCase(TestCase):
    def setUp(self):
        self.user_id = 1
        self.plan_name = "Basic"
        self.payment_details = {
            "method_type": PaymentMethodType.CREDIT_CARD.value,
            "card_number": "4242-4242-4242-4242",
            "expiration_date": "12/25",
            "cvc": "123",
        }

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

        response = self.service.subscribe_user_to_plan(
            user_id=self.user_id,
            plan_name=self.plan_name,
            payment_details=self.payment_details,
        )

        self.assertTrue(response["success"])
        self.assertIn("has subscribed to Basic plan successfully", response["message"])
        self.assertTrue(self.uow.committed)

    def test_subscribe_user_to_plan_with_invalid_plan(self):
        with self.assertRaises(ValueError) as context:
            self.service.subscribe_user_to_plan(
                user_id=123,
                plan_name="NonExistentPlan",
                payment_details={
                    "method_type": PaymentMethodType.CREDIT_CARD.value,
                    "card_number": "4242-4242-4242-4242",
                    "expiration_date": "12/25",
                    "cvc": "123",
                },
            )

            self.assertIsInstance(context, ValueError)

            self.assertFalse(self.uow.committed)
            self.assertTrue(self.uow.rolled_back)
