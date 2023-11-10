from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from subscription.serializers import SubscriptionRequestSerializer
from subscription.services import SubscriptionService
from subscription.unit_of_work import DjangoUnitOfWork


class SubscriptionViewSet(viewsets.ViewSet):
    uow = DjangoUnitOfWork()
    subscription_service = SubscriptionService(uow)

    @action(detail=False, methods=["post"], url_path="subscribe")
    def subscribe(self, request):
        serializer = SubscriptionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        valid_data = serializer.validated_data

        try:
            result = self.subscription_service.subscribe_user_to_plan(
                user_id=request.user.id,
                plan_name=valid_data["plan_name"],
                payment_details=valid_data["payment_details"],
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="cancel")
    def cancel(self, request):
        try:
            result = self.subscription_service.cancel_subscription(
                user_id=request.user.id
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="renew")
    def renew(self, request):
        try:
            result = self.subscription_service.renew_subscription(
                user_id=request.user.id
            )
        except ValueError as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="change-plan")
    def change(self, request):
        try:
            result = self.subscription_service.change_subscription_plan(
                user_id=request.user.id, new_plan_name=request.data["plan_name"]
            )
        except ValueError as e:
            print(e)
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(result, status=status.HTTP_200_OK)
