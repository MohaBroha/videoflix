from django.urls import path

from .views import ActivateAccountView, RegisterView, LoginView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path(
        "activate/<uidb64>/<token>/",
        ActivateAccountView.as_view(),
        name="activate",
    ),
]
