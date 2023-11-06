# repository.py

from typing import List, Optional

import subscription.domain_models as domain_models
import subscription.models as models


class DjangoUserSubscriptionRepository:
    def add(self, subscription: domain_models.UserSubscription):
        self.update(subscription)

    def get(self, user_id: int) -> Optional[domain_models.UserSubscription]:
        try:
            subscription = models.UserSubscription.objects.get(user_id=user_id)
            return subscription.to_domain()

        except models.UserSubscription.DoesNotExist:
            raise ValueError(f"Subscription for user {user_id} does not exist")

    def list(self) -> List[domain_models.UserSubscription]:
        return [
            django_subscription.to_domain()
            for django_subscription in models.UserSubscription.objects.all()
        ]

    def update(self, subscription: domain_models.UserSubscription):
        models.UserSubscription.update_from_domain(subscription)


class DjangoSubscriptionPlanRepository:
    def add(self, plan: domain_models.SubscriptionPlan):
        self.update(plan)

    def get(self, name: str) -> domain_models.SubscriptionPlan:
        try:
            plan = models.SubscriptionPlan.objects.get(name=name)
            return plan.to_domain()
        except models.SubscriptionPlan.DoesNotExist:
            raise ValueError(f"Plan {name} does not exist")

    def list(self) -> List[domain_models.SubscriptionPlan]:
        return [
            django_plan.to_domain()
            for django_plan in models.SubscriptionPlan.objects.all()
        ]

    def update(self, plan: domain_models.SubscriptionPlan):
        models.SubscriptionPlan.update_from_domain(plan)


class DjangoPaymentRepository:
    def add(self, payment: domain_models.Payment):
        self.update(payment)

    def get(self, id: int) -> domain_models.Payment:
        try:
            payment = models.Payment.objects.get(id=id)
            return payment.to_domain()
        except models.Payment.DoesNotExist:
            raise ValueError(f"Payment for  {id} does not exist")

    def get_list_by_user_id(self, user_id: int) -> domain_models.Payment:
        try:
            payments = models.Payment.objects.filter(subscription__user_id=user_id)
            return [payment.to_domain() for payment in payments]
        except models.Payment.DoesNotExist:
            raise ValueError(f"Payment for user {user_id} does not exist")

    def list(self) -> List[domain_models.Payment]:
        return [
            django_payment.to_domain()
            for django_payment in models.Payment.objects.all()
        ]

    def update(self, payment: domain_models.Payment):
        models.Payment.update_from_domain(payment)


class DjangoPaymentMethodRepository:
    def add(self, payment_method: domain_models.PaymentMethod):
        self.update(payment_method)

    def get(self, id: int) -> domain_models.PaymentMethod:
        try:
            payment_method = models.PaymentMethod.objects.get(id=id)
            return payment_method.to_domain()
        except models.PaymentMethod.DoesNotExist:
            raise ValueError(f"PaymentMethod for  {id} does not exist")

    def list(self) -> List[domain_models.PaymentMethod]:
        return [
            django_payment_method.to_domain()
            for django_payment_method in models.PaymentMethod.objects.all()
        ]

    def update(self, payment_method: domain_models.PaymentMethod):
        models.PaymentMethod.update_from_domain(payment_method)
