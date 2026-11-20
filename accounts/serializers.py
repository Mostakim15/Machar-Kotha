from typing import cast

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    """Validate registration data and create a Django User safely."""

    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password_confirm")
        read_only_fields = ("id",)
        extra_kwargs = {
            "username": {
                "required": True,
                "allow_blank": False,
            },
            "email": {
                "required": True,
                "allow_blank": False,
            },
        }

    def validate_email(self, email):
        """Normalize and ensure the email address is unique, ignoring case."""
        normalized_email = BaseUserManager.normalize_email(email)

        if User.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError(
                "A user with this email address already exists."
            )

        return normalized_email

    def validate(self, attrs):
        """Validate password confirmation and Django password rules."""
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": "Password confirmation does not match."}
            )

        # Pass a temporary User so Django can enforce username/email similarity.
        user = User(
            username=attrs.get("username", ""),
            email=attrs.get("email", ""),
        )

        try:
            validate_password(password=password, user=user)
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {"password": list(error.messages)}
            ) from error

        return attrs

    def create(self, validated_data):
        """Create the user with create_user(), which hashes the password."""
        validated_data.pop("password_confirm")

        password = validated_data.pop("password")

        return User.objects.create_user(
            password=password,
            **validated_data,
        )


class PasswordResetRequestSerializer(serializers.Serializer):
    """Start a password reset without revealing whether an email exists."""

    email = serializers.EmailField()

    def validate_email(self, email):
        """Normalize the email consistently with Django's User manager."""
        return BaseUserManager.normalize_email(email)

    def save(self, **kwargs):
        """
        Send reset instructions to a matching active user.

        PasswordResetForm intentionally performs the same response for unknown
        and active/inactive addresses, avoiding account enumeration.
        """
        validated_data = cast(dict[str, str], self.validated_data)
        form = PasswordResetForm({"email": validated_data["email"]})
        if form.is_valid():
            request = kwargs.get("request")
            if request is None:
                form.save(use_https=False)
            else:
                form.save(request=request, use_https=request.is_secure())

        return None


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Validate a reset token and set a new hashed password."""
    
    uid = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        """Resolve and validate the reset user and password."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Password confirmation does not match."}
            )

        try:
            user_id = force_str(
                urlsafe_base64_decode(attrs["uid"])
            )
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError(
                {"uid": "The password reset link is invalid."}
            )

        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError(
                {"token": "The password reset link is invalid or has expired."}
            )

        try:
            validate_password(password=attrs["password"], user=user)
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {"password": list(error.messages)}
            ) from error

        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        """Set the new password. Django set_password() performs hashing."""
        validated_data = cast(dict[str, object], self.validated_data)
        user = cast(User, validated_data["user"])
        password = cast(str, validated_data["password"])
        user.set_password(password)
        user.save(update_fields=["password"])
        return user
