from django.core.management.base import BaseCommand

from subscription.adapters.models import SubscriptionPlan


class Command(BaseCommand):
    help = "Initializes basic, standard, and premium subscription plans"

    def handle(self, *args, **kwargs):
        plans = [
            {
                "name": "basic",
                "price": "6000.00",
                "payment_cycle": "monthly",
                "description": "Basic plan description",
                "duration": "30 00:00:00",
            },
            {
                "name": "standard",
                "price": "11900.00",
                "payment_cycle": "monthly",
                "description": "Standard plan description",
                "duration": "30 00:00:00",
            },
            {
                "name": "premium",
                "price": "14900.00",
                "payment_cycle": "monthly",
                "description": "Premium plan description",
                "duration": "30 00:00:00",
            },
        ]
        for plan_data in plans:
            SubscriptionPlan.objects.get_or_create(**plan_data)
        self.stdout.write(
            self.style.SUCCESS("Successfully initialized subscription plans")
        )
