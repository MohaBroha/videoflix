from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.functions import (
    activate_user,
    create_activation_token,
    send_activation_email,
)
from .serializers import RegisterSerializer


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        uidb64, token = create_activation_token(user)
        send_activation_email(user, uidb64, token)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
                "token": token,
            },
            status=status.HTTP_201_CREATED,
        )


class ActivateAccountView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, uidb64, token):
        if activate_user(uidb64, token):
            return Response(
                {"message": "Account successfully activated."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": "Invalid activation link."},
            status=status.HTTP_400_BAD_REQUEST,
        )
