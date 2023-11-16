from datetime import date, timedelta
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase
from freezegun import freeze_time

from subscription.domain.domain_models import (
    PaymentCycle,
    PaymentMethodType,
    PlanName,
    SubscriptionPlan,
    SubscriptionStatus,
    UserSubscription,
)
from subscription.service_layer.services import SubscriptionService
from subscription.service_layer.unit_of_work import DjangoUnitOfWork
from subscription.tasks import renew_expired_subscriptions


class TaskTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "testuser", "test@example.com", "testpassword"
        )
        self.user2 = User.objects.create_user(
            "testuser2", "test2@example.com", "testpassword"
        )
        self.plan_name = PlanName.BASIC
        self.payment_details = {
            "method_type": PaymentMethodType.CREDIT_CARD.value,
            "card_number": "4242-4242-4242-4242",
            "expiration_date": "12/25",
            "cvc": "123",
        }
        self.plan = SubscriptionPlan(
            name=self.plan_name,
            price=10.00,
            payment_cycle=PaymentCycle.MONTHLY,
            description="Basic Plan",
            duration_days=30,
        )
        self.uow = DjangoUnitOfWork()
        self.service = SubscriptionService(self.uow)

    @mock.patch("random.choice")
    def test_renew_one_expiredsubscription(self, mock_random_choice):
        self.uow.subscription_plans.add(self.plan)
        self.uow.user_subscriptions.add(
            UserSubscription(
                user_id=self.user.id,
                plan=self.plan,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=self.plan.duration_days),
                status=SubscriptionStatus.ACTIVE,
            )
        )
        mock_random_choice.return_value = True
        self.uow.user_subscriptions.get_subscriptions_expiring_on(date.today())
        enddate = date.today() + timedelta(days=31)
        with freeze_time(enddate):
            task_result = renew_expired_subscriptions.apply()
            task_result.get()
            subscription_list = self.uow.user_subscriptions.list()
            self.assertEqual(len(subscription_list), 2)

    @mock.patch("random.choice")
    def test_renew_two_expired_subscription(self, mock_random_choice):
        self.uow.subscription_plans.add(self.plan)
        self.uow.user_subscriptions.add(
            UserSubscription(
                user_id=self.user.id,
                plan=self.plan,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=self.plan.duration_days),
                status=SubscriptionStatus.ACTIVE,
            )
        )
        self.uow.user_subscriptions.add(
            UserSubscription(
                user_id=self.user2.id,
                plan=self.plan,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=self.plan.duration_days),
                status=SubscriptionStatus.ACTIVE,
            )
        )
        self.uow.user_subscriptions.get_subscriptions_expiring_on(date.today())
        mock_random_choice.return_value = True
        enddate = date.today() + timedelta(days=31)
        with freeze_time(enddate):
            task_result = renew_expired_subscriptions.apply()
            task_result.get()
            subscription_list = self.uow.user_subscriptions.list()
            self.assertEqual(len(subscription_list), 4)
