from subscription.adapters.repository import TrackingRepository
from subscription.service_layer.unit_of_work import DjangoUnitOfWork


class FakeRepository:
    def __init__(self, items):
        self._items = set(items)

    def add(self, item):
        self._items.add(item)

    def get(self, identifier):
        try:
            return next(
                item for item in self._items if self.matches(item, "id", identifier)
            )
        except StopIteration:
            raise ValueError(f"Item with identifier {identifier} not found")

    def list(self):
        return list(self._items)

    def matches(self, item, fields, identifier):
        return item.__dict__[fields] == identifier


class FakeUserSubscriptionRepository(FakeRepository):
    def get_active_subscription_by_user_id(self, user_id: int):
        try:
            return next(
                item
                for item in self._items
                if item.user_id == user_id and item.status == "active"
            )
        except StopIteration:
            raise ValueError(f"Active subscription for user {user_id} not found")

    def update(self, item):
        pass


class FakeSubscriptionPlanRepository(FakeRepository):
    def matches(self, item, fields, identifier):
        return super().matches(item, "name", identifier)

    def get_by_id(self, id: int):
        self.matches = lambda item, fields, identifier: item.id == identifier
        return super().get(id)


class FakePaymentRepository(FakeRepository):
    pass


class FakePaymentMethodRepository(FakeRepository):
    pass


class FakeUnitOfWork(DjangoUnitOfWork):
    def __init__(self):
        self.user_subscriptions = TrackingRepository(FakeUserSubscriptionRepository([]))
        self.subscription_plans = TrackingRepository(FakeSubscriptionPlanRepository([]))
        self.payments = TrackingRepository(FakePaymentRepository([]))
        self.payment_methods = TrackingRepository(FakePaymentMethodRepository([]))
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.rollback()
            return False

        self.commit()
        return True

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True
