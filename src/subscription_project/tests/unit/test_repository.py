from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from subscription.domain_models import (
    PaymentCycle,
    PaymentMethodType,
    PaymentStatus,
    PlanName,
    SubscriptionStatus,
)
from subscription.domain_models import UserSubscription as DomainUserSubscription
from subscription.models import (
    Payment,
    PaymentMethod,
    SubscriptionPlan,
    UserSubscription,
)
from subscription.repository import (
    DjangoPaymentMethodRepository,
    DjangoPaymentRepository,
    DjangoUserSubscriptionRepository,
)


class DjangoUserSubscriptionRepositoryTest(TestCase):
    def setUp(self):
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

        self.domain_user_subscription = self.user_subscription.to_domain()

        self.repository = DjangoUserSubscriptionRepository()

    def test_add_subscription(self):
        # Test adding a new subscription
        new_plan = SubscriptionPlan.objects.create(
            name=PlanName.STANDARD.value,
            price="20.00",
            payment_cycle=PaymentCycle.MONTHLY.value,
            description="Standard Plan",
            duration=timedelta(days=30),
        )
        new_domain_subscription = DomainUserSubscription(
            user_id=self.user.id,
            plan_id=new_plan.id,
            start_date=date.today(),
            end_date=date.today(),
            status=SubscriptionStatus.ACTIVE,
        )
        self.repository.add(new_domain_subscription)
        created_subscription = UserSubscription.objects.get(
            user=self.user, plan=new_plan
        )
        self.assertIsNotNone(created_subscription)
        self.assertEqual(created_subscription.plan.name, new_plan.name)

    def test_get_subscription(self):
        # Test getting an existing subscription
        retrieved_subscription = self.repository.get_by_user_id(user_id=self.user.id)
        self.assertIsNotNone(retrieved_subscription)
        self.assertEqual(retrieved_subscription.user_id, self.user.id)

    def test_list_subscriptions(self):
        # Test listing all subscriptions
        subscriptions = self.repository.list()
        self.assertIsInstance(subscriptions, list)
        self.assertTrue(len(subscriptions) > 0)

    def test_update_subscription(self):
        # Test updating an existing subscription
        self.domain_user_subscription.status = SubscriptionStatus.EXPIRED
        self.repository.update(self.domain_user_subscription)
        updated_subscription = UserSubscription.objects.get(
            user=self.user, plan=self.plan
        )
        self.assertEqual(updated_subscription.status, SubscriptionStatus.EXPIRED.value)


class DjangoPaymentRepositoryTest(TestCase):
    def setUp(self):
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

        self.domain_user_subscription = DomainUserSubscription(
            user_id=self.user.id,
            plan_id=self.plan.id,
            start_date=date.today(),
            end_date=date.today(),
            status=SubscriptionStatus.ACTIVE,
        )

        self.payment_method = PaymentMethod.objects.create(
            method_type=PaymentMethodType.CREDIT_CARD.value,
            details={"card_number": "1234-1234-1234-1234"},
        )

        self.payment = Payment.objects.create(
            subscription=self.user_subscription,
            payment_method=self.payment_method,
            amount="10.00",
            date=date.today(),
            status=PaymentStatus.SUCCESS.value,
        )
        self.domian_payment = self.payment.to_domain()

        self.domian_payment_method = self.payment_method.to_domain()

        self.user_subscriptions = DjangoUserSubscriptionRepository()
        self.payments = DjangoPaymentRepository()
        self.payment_methods = DjangoPaymentMethodRepository()

    def test_get_payment(self):
        # Test getting an existing payment
        retrieved_payments = self.payments.get_list_by_user_id(user_id=self.user.id)
        self.assertIsNotNone(retrieved_payments)
        self.assertIsInstance(retrieved_payments, list)
        self.assertTrue(len(retrieved_payments) > 0)

    def test_list_payments(self):
        # Test listing all payments
        payments = self.payments.list()
        self.assertIsInstance(payments, list)
        self.assertTrue(len(payments) > 0)

    def test_update_payment(self):
        # Test updating an existing payment
        self.domian_payment.status = PaymentStatus.PENDING
        self.payments.update(self.domian_payment)
        updated_payment = Payment.objects.get(
            subscription=self.user_subscription, payment_method=self.payment_method
        )
        self.assertEqual(updated_payment.status, PaymentStatus.PENDING.value)

    def test_update_payment_method(self):
        # Test updating an existing payment method

        self.domian_payment_method.details = {"card_number": "1234-1234-1234-1234"}
        self.payment_methods.update(self.domian_payment_method)

        updated_payment_method = PaymentMethod.objects.get(
            method_type=PaymentMethodType.CREDIT_CARD.value
        )
        self.assertEqual(
            updated_payment_method.details, {"card_number": "1234-1234-1234-1234"}
        )
