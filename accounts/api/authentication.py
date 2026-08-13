from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate requests using a JWT stored in the access token cookie."""

    def authenticate(self, request):
        """Validate the request and return the authenticated user and token."""

        access_token = request.COOKIES.get("access_token")

        if not access_token:
            return None

        validated_token = self.get_validated_token(access_token)
        user = self.get_user(validated_token)

        return user, validated_token
