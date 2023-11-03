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

    name = models.CharField(max_length=100, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    description = models.TextField()
    duration = models.DurationField(help_text=_("Duration of the subscription plan"))

    def __str__(self):
        return self.name

    def to_domain(self) -> domain_models.SubscriptionPlan:
        return domain_models.SubscriptionPlan(
            name=self.name,
            price=float(self.price),
            description=self.description,
            duration_days=self.duration.days,
        )

    @staticmethod
    def update_from_domain(plan: domain_models.SubscriptionPlan):
        plan_django, _ = SubscriptionPlan.objects.get_or_create(name=plan.name.value)

        plan_django.price = Decimal(plan.price)
        plan_django.description = plan.description
        plan_django.duration = timedelta(days=plan.duration_days)
        plan_django.description = plan.description
        plan_django.save()


class UserSubscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriptions"
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.RESTRICT)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s subscription to {self.plan.name}"

    def to_domain(self) -> domain_models.UserSubscription:
        return domain_models.UserSubscription(
            user_id=self.user.id,
            plan=self.plan.to_domain(),
            start_date=self.start_date,
            end_date=self.end_date,
            active=self.active,
        )

    @staticmethod
    def update_from_domain(subscription: domain_models.UserSubscription):
        subscription_django, _ = UserSubscription.objects.get_or_create(
            user_id=subscription.user_id, plan__name=subscription.plan.name
        )

        subscription_django.start_date = subscription.start_date
        subscription_django.end_date = subscription.end_date
        subscription_django.active = subscription.active
        subscription_django.save()


class PaymentMethod(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payment_methods"
    )
    method_type = models.CharField(max_length=50)
    details = models.JSONField()

    def __str__(self):
        return f"{self.method_type} for {self.user.username}"

    def to_domain(self) -> domain_models.PaymentMethod:
        return domain_models.PaymentMethod(
            user_id=self.user.id,
            method_type=self.method_type,
            details=self.details,
        )

    @staticmethod
    def update_from_domain(payment_method: domain_models.PaymentMethod):
        payment_method_django, _ = PaymentMethod.objects.get_or_create(
            user_id=payment_method.user_id, method_type=payment_method.method_type
        )

        payment_method_django.details = payment_method.details
        payment_method_django.save()


class Payment(models.Model):
    subscription = models.ForeignKey(
        UserSubscription, on_delete=models.CASCADE, related_name="payments"
    )
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    date = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment of {self.amount} for {self.subscription.plan.name}"

    def to_domain(self) -> domain_models.Payment:
        return domain_models.Payment(
            subscription=self.subscription.to_domain(),
            payment_method=self.payment_method.to_domain(),
            amount=float(self.amount),
            date=self.date.date(),
            successful=self.successful,
        )

    @staticmethod
    def update_from_domain(payment: domain_models.Payment):
        payment_django, _ = Payment.objects.get_or_create(
            subscription__user_id=payment.subscription.user_id,
            subscription__plan__name=payment.subscription.plan.name,
            date=payment.date,
        )

        payment_django.amount = payment.amount
        payment_django.successful = payment.successful
        payment_django.save()
