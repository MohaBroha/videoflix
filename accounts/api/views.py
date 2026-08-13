from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.functions import (
    activate_user,
    create_activation_token,
    send_activation_email,
    send_password_reset_email,
)
from .serializers import (
    LoginSerializer,
    PasswordConfirmSerializer,
    PasswordResetSerializer,
    RegisterSerializer,
)


class RegisterView(APIView):
    """Register a new user account and send the activation email."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Create the user account and return the generated activation token."""

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
    """Activate a user account from an emailed token link."""

    authentication_classes = []
    permission_classes = []

    def get(self, request, uidb64, token):
        """Validate the activation link and set the user account to active."""

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
    """Authenticate a user and issue JWT cookies for the session."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Validate user credentials and return a successful login response."""

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
    """Log out a user by invalidating the refresh token and clearing cookies."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Blacklist the refresh token and remove authentication cookies."""

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


class TokenRefreshView(APIView):
    """Issue a new access token from a valid refresh token in the cookie."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Refresh the JWT access token and return it in the response cookie."""

        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
        except Exception:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response(
            {
                "detail": "Token refreshed",
                "access": access_token,
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
        )

        return response


class PasswordResetView(APIView):
    """Request a password reset link for a registered user."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Send a reset email when the submitted email exists in the system."""

        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        User = get_user_model()
        user = User.objects.get(email=serializer.validated_data["email"])

        uidb64, token = create_activation_token(user)
        send_password_reset_email(user, uidb64, token)

        return Response(
            {"detail": "An email has been sent to reset your password."},
            status=status.HTTP_200_OK,
        )


class PasswordConfirmView(APIView):
    """Set a new password from a valid password reset token."""

    authentication_classes = []
    permission_classes = []

    def post(self, request, uidb64, token):
        """Validate the reset link and save the new password for the user."""

        serializer = PasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            return Response(
                {"detail": "Invalid password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        return Response(
            {"detail": "Your Password has been successfully reset."},
            status=status.HTTP_200_OK,
        )
