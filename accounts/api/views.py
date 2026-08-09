from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.functions import (
    activate_user,
    create_activation_token,
    send_activation_email,
)
from .serializers import RegisterSerializer, LoginSerializer


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


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                "detail": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            "access_token",
            str(refresh.access_token),
            httponly=True,
        )
        response.set_cookie(
            "refresh_token",
            str(refresh),
            httponly=True,
        )

        return response


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        response = Response(
            {
                "detail": (
                    "Logout successful! All tokens will be deleted. "
                    "Refresh token is now invalid."
                )
            },
            status=status.HTTP_200_OK,
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response
