from django.urls import path

from .views import (
    ActivateAccountView,
    LoginView,
    LogoutView,
    RegisterView,
    TokenRefreshView,
    PasswordResetView,
    PasswordConfirmView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "activate/<uidb64>/<token>/",
        ActivateAccountView.as_view(),
        name="activate",
    ),
    path(
        "password_reset/",
        PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password_confirm/<uidb64>/<token>/",
        PasswordConfirmView.as_view(),
        name="password_confirm",
    ),
]
