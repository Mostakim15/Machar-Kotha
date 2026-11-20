from django.urls import path

from accounts import views


app_name = 'accounts'

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "password/reset/",
        views.PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password/reset/confirm/",
        views.PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]
