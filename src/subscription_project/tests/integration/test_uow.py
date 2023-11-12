from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from subscription.adapters.models import SubscriptionPlan, UserSubscription
from subscription.domain.domain_models import PaymentCycle, PlanName
from subscription.domain.domain_models import SubscriptionPlan as DomainSubscriptionPlan
from subscription.domain.domain_models import SubscriptionStatus
from subscription.domain.domain_models import UserSubscription as DomainUserSubscription
from subscription.unit_of_work import DjangoUnitOfWork


class TestDjangoUnitOfWork(TestCase):
    def setUp(self):
        # 필요한 테스트 데이터를 설정합니다.
        self.user = User.objects.create_user(
            "testuser", "test@example.com", "testpassword"
        )
        self.plan = SubscriptionPlan.objects.create(
            name=PlanName.BASIC.value,
            price="10.00",
            payment_cycle=PaymentCycle.MONTHLY.value,
            description="Basic Plan",
            duration=timedelta(days=30),
        )
        self.user_subscription = UserSubscription.objects.create(
            user=self.user,
            plan=self.plan,
            start_date=date.today(),
            end_date=date.today(),
            status=SubscriptionStatus.ACTIVE.value,
        )

    def test_adding_user_subscription(self):
        uow = DjangoUnitOfWork()
        with uow:
            subscription = DomainUserSubscription(
                user_id=self.user.id,
                plan=self.plan,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=self.plan.duration.days),
                status=SubscriptionStatus.ACTIVE,
            )

            uow.user_subscriptions.add(subscription)
            uow.commit()

        # 데이터베이스 상태를 검증합니다.
        with uow:
            saved_subscription = uow.user_subscriptions.get_by_user_id(
                subscription.user_id
            )
            self.assertIsNotNone(saved_subscription)
            self.assertEqual(saved_subscription.user_id, subscription.user_id)
            self.assertEqual(saved_subscription.plan.id, subscription.plan.id)
            self.assertEqual(saved_subscription.status, subscription.status)

            uow.commit()

    def test_rollback_user_subscription(self):
        uow = DjangoUnitOfWork()
        with self.assertRaises(Exception):
            with uow:
                subscription = DomainUserSubscription(
                    user_id=1,
                    plan=self.plan,
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=self.plan.duration.days),
                    status=SubscriptionStatus.ACTIVE,
                )

                uow.user_subscriptions.add(subscription)

                raise Exception("Force rollback")

        with uow:
            saved_subscription = uow.user_subscriptions.get_by_user_id(
                subscription.user_id
            )
            self.assertIsNone(saved_subscription)
