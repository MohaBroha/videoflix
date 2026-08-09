from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth import authenticate

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "confirmed_password")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError(
                "Bitte überprüfe deine Eingaben und versuche es erneut."
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirmed_password")
        return User.objects.create_user(
            is_active=False,
            **validated_data,
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
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
