# repository.py

from typing import Generic, Iterable, List, Optional, Protocol, Set, TypeVar

import subscription.adapters.models as models
import subscription.domain.domain_models as domain_models

T = TypeVar("T")


class AbstractRepository(Protocol, Generic[T]):
    def add(self, obj: T):
        ...

    def get(self, id: int) -> T:
        ...

    def list(self) -> List[T]:
        ...

    def update(self, obj: T):
        ...


class TrackingRepository:
    seen: Set[T]

    def __init__(self, repo: AbstractRepository):
        self.seen = set()  # type: Set[domain_model.T]
        self._repo = repo

    def add(self, obj: T):
        self._repo.add(obj)
        self.seen.add(obj)

    def get(self, id) -> Optional[T]:
        obj = self._repo.get(id)
        if obj:
            self.seen.add(obj)
        return obj

    # NOTE: 이 메서드는 래핑된 리포지토리의 get,add 이외의 메서드가 호출될 때 사용된다.
    def __getattr__(self, name: str):
        def wrapper(*args, **kwargs):
            result = getattr(self._repo, name)(*args, **kwargs)
            if isinstance(result, Iterable) and not isinstance(result, str):
                for item in result:
                    self.seen.add(item)
            else:
                self.seen.add(result)
            return result

        return wrapper


class DjangoUserSubscriptionRepository(
    AbstractRepository[domain_models.UserSubscription]
):
    def add(self, subscription: domain_models.UserSubscription):
        self.update(subscription)

    def get(self, subscription_id: int) -> Optional[domain_models.UserSubscription]:
        try:
            subscription = models.UserSubscription.objects.get(id=subscription_id)
            return subscription.to_domain()

        except models.UserSubscription.DoesNotExist:
            raise ValueError(f"Subscription for  {subscription_id} does not exist")

    def get_by_user_id(self, user_id: int) -> Optional[domain_models.UserSubscription]:
        queryset = models.UserSubscription.objects.filter(user_id=user_id)

        django_subscription = queryset.first()

        if django_subscription:
            return django_subscription.to_domain()
        else:
            return None

    def list(self) -> List[domain_models.UserSubscription]:
        return [
            django_subscription.to_domain()
            for django_subscription in models.UserSubscription.objects.all()
        ]

    def update(self, subscription: domain_models.UserSubscription):
        models.UserSubscription.update_from_domain(subscription)

    def get_active_subscription_by_user_id(
        self, user_id: int
    ) -> Optional[domain_models.UserSubscription]:
        try:
            active_subscription = (
                models.UserSubscription.objects.filter(
                    user_id=user_id,
                    status=domain_models.SubscriptionStatus.ACTIVE.value,
                )
                .order_by("-start_date")
                .first()
            )
            return active_subscription.to_domain() if active_subscription else None
        except models.UserSubscription.DoesNotExist:
            return None


class DjangoSubscriptionPlanRepository(
    AbstractRepository[domain_models.SubscriptionPlan]
):
    def add(self, plan: domain_models.SubscriptionPlan):
        self.update(plan)

    def get(self, name: str) -> domain_models.SubscriptionPlan:
        try:
            plan = models.SubscriptionPlan.objects.get(name=name)
            return plan.to_domain()
        except models.SubscriptionPlan.DoesNotExist:
            raise ValueError(f"Plan {name} does not exist")

    def get_by_id(self, id: int) -> domain_models.SubscriptionPlan:
        try:
            plan = models.SubscriptionPlan.objects.get(id=id)
            return plan.to_domain()
        except models.SubscriptionPlan.DoesNotExist:
            raise ValueError(f"Plan {id} does not exist")

    def list(self) -> List[domain_models.SubscriptionPlan]:
        return [
            django_plan.to_domain()
            for django_plan in models.SubscriptionPlan.objects.all()
        ]

    def update(self, plan: domain_models.SubscriptionPlan):
        models.SubscriptionPlan.update_from_domain(plan)


class DjangoPaymentRepository(AbstractRepository[domain_models.Payment]):
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


class DjangoPaymentMethodRepository(AbstractRepository[domain_models.PaymentMethod]):
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
