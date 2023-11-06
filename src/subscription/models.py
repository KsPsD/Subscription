from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import domain_models


class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ("basic", _("Basic Plan")),
        ("standard", _("Standard Plan")),
        ("premium", _("Premium Plan")),
    ]
    PAYMENT_CYCLE_CHOICES = [
        ("monthly", _("Monthly")),
        ("yearly", _("Yearly")),
        ("once", _("Once")),
    ]

    name = models.CharField(max_length=100, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    payment_cycle = models.CharField(max_length=10, choices=PAYMENT_CYCLE_CHOICES)
    description = models.TextField()
    duration = models.DurationField(help_text=_("Duration of the subscription plan"))

    def __str__(self):
        return self.name

    def to_domain(self) -> domain_models.SubscriptionPlan:
        return domain_models.SubscriptionPlan(
            name=domain_models.PlanName(self.name),
            price=float(self.price),
            payment_cycle=domain_models.PaymentCycle(self.payment_cycle),
            description=self.description,
            duration_days=self.duration.days,
        )

    @staticmethod
    def update_from_domain(plan: domain_models.SubscriptionPlan):
        plan_django, _ = SubscriptionPlan.objects.get_or_create(name=plan.name.value)

        plan_django.price = Decimal(plan.price)
        plan_django.payment_cycle = plan.payment_cycle.value
        plan_django.description = plan.description
        plan_django.duration = timedelta(days=plan.duration_days)
        plan_django.save()


class UserSubscription(models.Model):
    SUBSCRIPTION_STATUS_CHOICES = [
        ("active", _("Active")),
        ("expired", _("Expired")),
        ("pending", _("Pending")),
        # 기타 필요한 상태를 추가할 수 있습니다.
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.RESTRICT)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=10, choices=SUBSCRIPTION_STATUS_CHOICES, default="pending"
    )

    def __str__(self):
        return f"{self.user.username}'s subscription to {self.plan.name}"

    def to_domain(self) -> domain_models.UserSubscription:
        return domain_models.UserSubscription(
            user_id=self.user.id,
            plan_id=self.plan.id,
            start_date=self.start_date,
            end_date=self.end_date,
            status=domain_models.SubscriptionStatus(self.status),
        )

    @staticmethod
    def update_from_domain(subscription: domain_models.UserSubscription):
        subscription_django, _ = UserSubscription.objects.get_or_create(
            user_id=subscription.user_id,
            plan_id=subscription.plan_id,
            start_date=subscription.start_date,
            end_date=subscription.end_date,
        )

        subscription_django.status = subscription.status.value
        subscription_django.save()


class PaymentMethod(models.Model):
    method_type = models.CharField(max_length=50)
    details = models.JSONField()

    def __str__(self):
        return f"{self.method_type}"

    def to_domain(self) -> domain_models.PaymentMethod:
        return domain_models.PaymentMethod(
            method_type=domain_models.PaymentMethodType(self.method_type),
            details=self.details,
        )

    @staticmethod
    def update_from_domain(payment_method: domain_models.PaymentMethod):
        payment_method_django, _ = PaymentMethod.objects.get_or_create(
            method_type=payment_method.method_type.value
        )

        payment_method_django.details = payment_method.details
        payment_method_django.save()


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("canceled", "Canceled"),
        ("refunded", "Refunded"),
    ]
    subscription = models.ForeignKey(
        UserSubscription, on_delete=models.CASCADE, related_name="payments"
    )
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    date = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"Payment of {self.amount} for {self.subscription.plan.name} of {self.subscription.user.username}"

    def to_domain(self) -> domain_models.Payment:
        return domain_models.Payment(
            subscription_id=self.subscription.id,
            payment_method_id=self.payment_method.id,
            amount=float(self.amount),
            date=self.date.date(),
            status=domain_models.PaymentStatus(self.status),
        )

    @staticmethod
    def update_from_domain(payment: domain_models.Payment):
        payment_django, _ = Payment.objects.get_or_create(
            subscription_id=payment.subscription.id,
            payment_method_id=payment.payment_method.id,
            date=payment.date,
        )

        payment_django.amount = payment.amount
        payment_django.status = payment.status.value
        payment_django.save()
