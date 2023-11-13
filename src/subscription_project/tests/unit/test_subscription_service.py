from datetime import date
from unittest import mock

from django.test import TestCase

from subscription.domain.domain_models import (
    PaymentMethodType,
    SubscriptionPlan,
    SubscriptionStatus,
    UserSubscription,
)
from subscription.domain.events import PaymentFailed
from subscription.service_layer.services import SubscriptionService
from subscription.service_layer.unit_of_work import DjangoUnitOfWork
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
        self.plan = SubscriptionPlan(
            name=self.plan_name,
            price=10.00,
            payment_cycle="monthly",
            description="Basic Plan",
            duration_days=30,
        )
        self.uow = FakeUnitOfWork()
        self.service = SubscriptionService(self.uow)

    @mock.patch("random.choice")
    def test_process_payment_with_mark_failed(self, mock_random_choice):
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
        mock_random_choice.return_value = False

        response = self.service.process_payment(
            user_id=self.user_id,
            amount=10.00,
        )
        self.assertFalse(response[0])
        self.assertEqual(type(response[1].events[0]), PaymentFailed)
