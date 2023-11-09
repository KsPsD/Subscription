import json
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.forms import ValidationError
from django.urls import reverse
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from subscription.domain_models import PaymentCycle, PlanName, SubscriptionPlan
from subscription.repository import DjangoSubscriptionPlanRepository


class SubscriptionViewSetTest(APITestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(
            "testuser", "test@example.com", "testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.plan_repository = DjangoSubscriptionPlanRepository()
        self.test_plan = SubscriptionPlan(
            name=PlanName.BASIC,
            price=9.99,
            duration_days=30,
            payment_cycle=PaymentCycle.MONTHLY,
            description="Test Plan",
        )
        self.plan_repository.add(plan=self.test_plan)

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
        self.assertFalse(response.data["success"])

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
            self.assertTrue(response.data["success"])
