from subscription.unit_of_work import DjangoUnitOfWork


class FakeRepository:
    def __init__(self, items):
        self._items = set(items)

    def add(self, item):
        self._items.add(item)

    def get(self, identifier):
        try:
            return next(item for item in self._items if self.matches(item, identifier))
        except StopIteration:
            raise ValueError(f"Item with identifier {identifier} not found")

    def list(self):
        return list(self._items)

    def matches(self, item, identifier):
        return item.id == identifier


class FakeUserSubscriptionRepository(FakeRepository):
    pass


class FakeSubscriptionPlanRepository(FakeRepository):
    def matches(self, item, identifier):
        return item.name == identifier


class FakePaymentRepository(FakeRepository):
    pass


class FakePaymentMethodRepository(FakeRepository):
    pass


class FakeUnitOfWork(DjangoUnitOfWork):
    def __init__(self):
        self.user_subscriptions = FakeUserSubscriptionRepository([])
        self.subscription_plans = FakeSubscriptionPlanRepository([])
        self.payments = FakePaymentRepository([])
        self.payment_methods = FakePaymentMethodRepository([])
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

    def collect_new_events(self):
        pass
