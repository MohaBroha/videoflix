from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

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


def _get_logo_path():
    """Return the path to the Videoflix email logo."""

    return Path(settings.BASE_DIR) / "accounts" / "templates" / "emails" / "Logo.svg"


def _attach_logo(email):
    """Attach the Videoflix logo as an inline email image."""

    from email.mime.base import MIMEBase
    from email import encoders

    logo_path = _get_logo_path()

    with logo_path.open("rb") as logo_file:
        logo = MIMEBase("image", "svg+xml")
        logo.set_payload(logo_file.read())

    encoders.encode_base64(logo)

    logo.add_header(
        "Content-ID",
        "<videoflix-logo>",
    )
    logo.add_header(
        "Content-Disposition",
        "inline",
        filename="Logo.svg",
    )

    email.attach(logo)


def send_activation_email(user, uidb64, token):
    """Send the account activation email to the provided user."""

    activation_url = (
        f"{settings.FRONTEND_URL}"
        f"/pages/auth/activate.html?uid={uidb64}&token={token}"
    )

    html_content = render_to_string(
        "emails/confirm_email.html",
        {
            "user": user,
            "activation_url": activation_url,
        },
    )

    text_content = (
        "Welcome to Videoflix!\n\n"
        "Please confirm your email address using the following link:\n"
        f"{activation_url}\n\n"
        "If you did not register for Videoflix, you can ignore this email."
    )

    email = EmailMultiAlternatives(
        subject="Confirm your Videoflix email",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.attach_alternative(html_content, "text/html")
    _attach_logo(email)
    email.send()


def send_password_reset_email(user, uidb64, token):
    """Send the password reset email to the provided user."""

    reset_url = (
        f"{settings.FRONTEND_URL}"
        f"/pages/auth/confirm_password.html?uid={uidb64}&token={token}"
    )

    html_content = render_to_string(
        "emails/password_reset.html",
        {
            "user": user,
            "reset_url": reset_url,
        },
    )

    text_content = (
        "You requested a password reset for your Videoflix account.\n\n"
        "Please reset your password using the following link:\n"
        f"{reset_url}\n\n"
        "If you did not request a password reset, you can ignore this email."
    )

    email = EmailMultiAlternatives(
        subject="Reset your Videoflix password",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.attach_alternative(html_content, "text/html")
    _attach_logo(email)
    email.send()
