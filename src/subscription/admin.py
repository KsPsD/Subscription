from django.contrib import admin

from subscription.adapters.models import (
    Payment,
    PaymentMethod,
    SubscriptionPlan,
    UserSubscription,
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "payment_cycle",
        "description",
        "duration",
    )
    list_filter = ("payment_cycle",)
    search_fields = ("name", "description")


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "start_date", "end_date", "status")
    list_filter = ("status", "plan")
    search_fields = ("user__username", "plan__name")


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("method_type", "details")
    search_fields = ("method_type",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("subscription", "payment_method", "amount", "date", "status")
    list_filter = ("status", "payment_method")
    search_fields = ("subscription__user__username", "payment_method__method_type")
