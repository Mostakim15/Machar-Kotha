from typing import cast

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIRequestFactory, APITestCase
from unittest.mock import patch

from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
)


class RegisterSerializerTests(APITestCase):
    def test_registers_user_and_hashes_password(self):
        serializer = RegisterSerializer(
            data={
                "username": "testuser",
                "email": "TestUser@Example.COM",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = cast(User, serializer.save())

        self.assertNotEqual(user.password, "StrongPass123!")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertEqual(user.email, "TestUser@example.com")

    def test_rejects_password_confirmation_mismatch(self):
        serializer = RegisterSerializer(
            data={
                "username": "testuser",
                "email": "test@example.com",
                "password": "StrongPass123!",
                "password_confirm": "DifferentPass123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)

    def test_rejects_duplicate_email_case_insensitively(self):
        User.objects.create_user(
            username="existing",
            email="test@example.com",
            password="StrongPass123!",
        )
        serializer = RegisterSerializer(
            data={
                "username": "newuser",
                "email": "TEST@EXAMPLE.COM",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class PasswordResetSerializerTests(APITestCase):
    def test_password_reset_request_uses_django_reset_form(self):
        User.objects.create_user(
            username="resetuser",
            email="reset@example.com",
            password="OldStrongPass123!",
        )
        request = APIRequestFactory().post("/api/accounts/password/reset/")
        serializer = PasswordResetRequestSerializer(
            data={"email": "RESET@example.com"}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        with patch(
            "accounts.serializers.PasswordResetForm.save"
        ) as mock_save:
            result = serializer.save(request=request)

        self.assertIsNone(result)
        mock_save.assert_called_once_with(
            request=request,
            use_https=False,
        )

    def test_password_reset_confirm_changes_password(self):
        user = User.objects.create_user(
            username="resetuser",
            email="reset@example.com",
            password="OldStrongPass123!",
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        serializer = PasswordResetConfirmSerializer(
            data={
                "uid": uid,
                "token": token,
                "password": "NewStrongPass456!",
                "password_confirm": "NewStrongPass456!",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        reset_user = cast(User, serializer.save())

        reset_user.refresh_from_db()
        self.assertTrue(reset_user.check_password("NewStrongPass456!"))
        self.assertFalse(reset_user.check_password("OldStrongPass123!"))

    def test_password_reset_confirm_rejects_invalid_token(self):
        user = User.objects.create_user(
            username="resetuser",
            email="reset@example.com",
            password="OldStrongPass123!",
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        serializer = PasswordResetConfirmSerializer(
            data={
                "uid": uid,
                "token": "invalid-token",
                "password": "NewStrongPass456!",
                "password_confirm": "NewStrongPass456!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("token", serializer.errors)
