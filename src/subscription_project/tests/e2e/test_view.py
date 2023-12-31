import json
from datetime import date, timedelta
from unittest import mock

from django.contrib.auth.models import User
from django.urls import reverse
from freezegun import freeze_time
from rest_framework import serializers, status
from rest_framework.test import APITestCase

from subscription.adapters.repository import DjangoSubscriptionPlanRepository
from subscription.domain.domain_models import PaymentCycle, PlanName, SubscriptionPlan


class SubscriptionViewSetTest(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(
            "admin", "admin@example.com", "password"
        )
        self.client.login(username="admin", password="password")
        self.plan_repository = DjangoSubscriptionPlanRepository()
        self.test_plan = SubscriptionPlan(
            name=PlanName.BASIC,
            price=9.99,
            duration_days=30,
            payment_cycle=PaymentCycle.MONTHLY,
            description="Test Plan",
        )
        self.plan_repository.add(plan=self.test_plan)
        self.plan_repository.add(
            plan=SubscriptionPlan(
                name=PlanName.PREMIUM,
                price=19.99,
                duration_days=30,
                payment_cycle=PaymentCycle.MONTHLY,
                description="Test Plan",
            )
        )

    def test_subscribe_to_plan(self):
        """
        Test subscribing to a plan successfully.
        """
        url = reverse("subscription-subscribe")
        data = {
            "plan_name": self.test_plan.name,
            "payment_details": {
                "method_type": "credit_card",
                "card_number": "4242-4242-4242-4242",
                "expiration_date": "12/25",
                "cvc": "123",
            },
        }
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    def test_subscribe_to_nonexistent_plan(self):
        url = reverse("subscription-subscribe")
        data = {
            "plan_name": "Nonexistent Plan",
            "payment_details": {
                "card_number": "4242-4242-4242-4242",
                "expiration_date": "12/25",
                "cvc": "123",
            },
        }
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscribe_to_wrong_card_number(self):
        url = reverse("subscription-subscribe")
        data = {
            "plan_name": self.test_plan.name,
            "payment_details": {
                "method_type": "credit_card",
                "card_number": "1234-1234-1234-1234",
                "expiration_date": "12/25",
                "cvc": "123",
            },
        }

        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("card_number", response.data["payment_details"])

    def test_cancel_subscribe(self):
        """
        Test cancelling subscription successfully.
        """

        url = reverse("subscription-subscribe")
        data = {
            "plan_name": self.test_plan.name,
            "payment_details": {
                "method_type": "credit_card",
                "card_number": "4242-4242-4242-4242",
                "expiration_date": "12/25",
                "cvc": "123",
            },
        }
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        url = reverse("subscription-cancel")
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

    def test_renew_subscribe(self):
        """
        Test renewing subscription successfully.
        """
        url = reverse("subscription-subscribe")
        data = {
            "plan_name": self.test_plan.name,
            "payment_details": {
                "method_type": "credit_card",
                "card_number": "4242-4242-4242-4242",
                "expiration_date": "12/25",
                "cvc": "123",
            },
        }
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        renew_date = date.today() + timedelta(days=31)

        with freeze_time(renew_date):
            self.client.login(username="testuser", password="testpassword")
            url = reverse("subscription-renew")
            response = self.client.post(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_subscribe(self):
        """
        Test changing subscription successfully.
        """
        url = reverse("subscription-subscribe")
        data = {
            "plan_name": self.test_plan.name,
            "payment_details": {
                "method_type": "credit_card",
                "card_number": "4242-4242-4242-4242",
                "expiration_date": "12/25",
                "cvc": "123",
            },
        }
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        with mock.patch(
            "random.choice",
            return_value=True,
        ) as mock_change_subscription_plan:
            url = reverse("subscription-change")
            data = {"plan_name": "premium"}
            response = self.client.post(
                url, data=json.dumps(data), content_type="application/json"
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data["success"])
