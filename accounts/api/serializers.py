from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth import authenticate

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Validate and create a new user account from registration input."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        """Configure the model and fields exposed by the serializer."""

        model = User
        fields = ("email", "password", "confirmed_password")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, attrs):
        """Ensure the password matches the confirmation field."""

        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError(
                "Bitte überprüfe deine Eingaben und versuche es erneut."
            )
        return attrs

    def create(self, validated_data):
        """Create an inactive user account from the validated registration data."""

        validated_data.pop("confirmed_password")
        return User.objects.create_user(
            is_active=False,
            **validated_data,
        )


class LoginSerializer(serializers.Serializer):
    """Validate email and password credentials for account sign-in."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the user and verify the account is active."""

        email = attrs["email"]
        password = attrs["password"]

        user = authenticate(
            username=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                "Bitte überprüfe deine Eingaben und versuche es erneut."
            )

        if not user.is_active:
            raise serializers.ValidationError("Bitte aktiviere zuerst dein Konto.")

        attrs["user"] = user
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    """Validate the email address before sending a password reset link."""

    email = serializers.EmailField()

    def validate_email(self, value):
        """Check whether the provided email belongs to a registered user."""

        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value


class PasswordConfirmSerializer(serializers.Serializer):
    """Validate the password reset confirmation input."""

    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        """Ensure the new password matches the confirmation field."""

        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
