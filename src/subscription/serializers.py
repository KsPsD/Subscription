import calendar
from datetime import datetime

from rest_framework import serializers

from subscription.domain_models import Card


class PaymentDetailsSerializer(serializers.Serializer):
    method_type = serializers.CharField(required=False, default="credit_card")
    card_number = serializers.CharField(required=True, max_length=19, min_length=19)
    expiration_date = serializers.DateField(
        required=True, format="%m/%y", input_formats=["%m/%y"]
    )
    cvc = serializers.CharField(required=True, max_length=4, min_length=3)

    def validate_card_number(self, value):
        # Luhn 알고리즘을 이용한 카드 번호 검증

        def luhn_checksum(card_number):
            def digits_of(n):
                return [int(d) for d in str(n) if d.isdigit()]

            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10

        card_number = value.replace(" ", "")  # 공백 제거

        if luhn_checksum(card_number):
            raise serializers.ValidationError("Invalid card number")

        return value

    def validate_cvc(self, value):
        # CVC 검증 로직
        if not value.isdigit():
            raise serializers.ValidationError("CVC must contain only digits.")
        return value

    def validate_expiration_date(self, value):
        last_day_of_month = calendar.monthrange(value.year, value.month)[1]
        expiration_date = datetime(value.year, value.month, last_day_of_month)
        if expiration_date < datetime.now():
            raise serializers.ValidationError("The card's expiration date has passed.")
        return value


class CardSerializer(serializers.Serializer):
    card_number = serializers.CharField()
    card_expiry = serializers.DateField(
        format="%Y-%m-%dT%H:%M:%S.%fZ", input_formats=["%m/%y", "%Y-%m-%dT%H:%M:%S.%fZ"]
    )
    card_cvc = serializers.CharField()

    def create(self, validated_data):
        return Card(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance

    def validate(self, data):
        return data


class SubscriptionRequestSerializer(serializers.Serializer):
    plan_name = serializers.CharField(required=True)
    payment_details = PaymentDetailsSerializer(required=True)

    def validate(self, data):
        return data
