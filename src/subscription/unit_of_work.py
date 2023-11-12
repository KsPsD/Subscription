from __future__ import annotations

import abc

from django.db import transaction

from .adapters.repository import (
    DjangoPaymentMethodRepository,
    DjangoPaymentRepository,
    DjangoSubscriptionPlanRepository,
    DjangoUserSubscriptionRepository,
    TrackingRepository,
)


class AbstractUnitOfWork(abc.ABC):
    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    @abc.abstractmethod
    def collect_new_events(self):
        raise NotImplementedError


class DjangoUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.user_subscriptions = TrackingRepository(DjangoUserSubscriptionRepository())
        self.subscription_plans = TrackingRepository(DjangoSubscriptionPlanRepository())
        self.payments = TrackingRepository(DjangoPaymentRepository())
        self.payment_methods = TrackingRepository(DjangoPaymentMethodRepository())

    def __enter__(self):
        self._transaction = transaction.atomic()
        self._transaction.__enter__()
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self._transaction.__exit__(exc_type, exc_value, traceback)
            return False
        # 잘 실행 됐으면 커밋 하고 종료
        self._transaction.__exit__(None, None, None)
        return True

    def commit(self):
        pass

    def rollback(self):
        pass

    def collect_new_events(self):
        # NOTE: UoW중 발생한 도메인 이벤트를 수집하는 메서드 나중에 구현
        pass
