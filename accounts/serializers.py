from rest_framework import serializers
from accounts.models import MyUser
from django.utils.encoding import force_bytes, smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = MyUser
        fields = ('email', 'name', 'tc','password','password_confirm',)
        extra_kwargs = {'password': {'write_only': True}}

#validate password and confirm password
    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError("Password and Confirm Password do not match.")
        return attrs

#create user do 
    def create(self, validated_data):
      return MyUser.object.create_user(**validated_data)

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = MyUser
        fields = ('email', 'password',)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('id', 'email', 'name',)

class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError("New Password and Confirm New Password do not match.")
        return attrs

class SendPasswordResetEmailViewSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if MyUser.object.filter(email=email).exists():
            user = MyUser.object.get(email=email)
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = f'http://localhost:3000/api/user/reset-password/{uidb64}/{token}'
            # Send email to user with the link
            data = {'email_body': f'Click the link to reset your password: {link}', 'to_email': user.email, 'email_subject': 'Reset your password'}
            return attrs
        else:
            raise serializers.ValidationError('You are not a registered user')

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    password_confirm = serializers.CharField(min_length=6, max_length=68, write_only=True)

    class Meta:
        fields = ['password', 'password_confirm']

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        uid = self.context.get('uid')
        token = self.context.get('token')
        if not uid or not token:
            raise serializers.ValidationError('Invalid password reset link.')    
        try:
            id = smart_str(urlsafe_base64_decode(uid))
            user = MyUser.object.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('The reset link is invalid', 401)
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError('The reset link is invalid', 401)
        if password != password_confirm:
            raise serializers.ValidationError("Password and Confirm Password do not match.")
        user.set_password(password)
        user.save()
        return attrs