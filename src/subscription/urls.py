# your_app/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from subscription.views.api import SubscriptionViewSet

router = DefaultRouter()

router.register(r"subscriptions", SubscriptionViewSet, basename="subscription")

urlpatterns = [
    path("", include(router.urls)),
]
