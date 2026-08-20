from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

User = get_user_model()


def create_activation_token(user):
    """Create a signed activation token and UID for the given user."""

    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    return uidb64, token


def activate_user(uidb64, token):
    """Activate a user when the provided token and UID are valid."""

    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return False

    if not default_token_generator.check_token(user, token):
        return False

    user.is_active = True
    user.save(update_fields=["is_active"])
    return True


def send_activation_email(user, uidb64, token):
    """Send the account activation email to the provided user."""

    activation_url = (
        f"{settings.FRONTEND_URL}"
        f"/pages/auth/activate.html?uid={uidb64}&token={token}"
    )

    send_mail(
        subject="Activate your Videoflix account",
        message=(
            "Welcome to Videoflix!\n\n"
            "Please activate your account using the following link:\n"
            f"{activation_url}\n\n"
            "If you did not register for Videoflix, you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


def send_password_reset_email(user, uidb64, token):
    """Send a password reset email to the provided user."""

    reset_url = (
        f"{settings.FRONTEND_URL}"
        f"/pages/auth/confirm_password.html?uid={uidb64}&token={token}"
    )

    send_mail(
        subject="Reset your Videoflix password",
        message=(
            "You requested a password reset for your Videoflix account.\n\n"
            "Please reset your password using the following link:\n"
            f"{reset_url}\n\n"
            "If you did not request a password reset, you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
