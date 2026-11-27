from typing import cast 

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from accounts.serializers import UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserProfileSerializer, UserRegistrationSerializer, SendPasswordResetEmailViewSerializer
from django.contrib.auth import authenticate
from accounts.renderers import CustomJSONRenderer
from rest_framework.permissions import IsAuthenticated



#Generate token manually using rest_framework_simplejwt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed

def get_tokens_for_user(user):
    if not user.is_active:
      raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegistrationView(APIView):
    renderer_classes = [CustomJSONRenderer]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({'message': 'User registered successfully', 'token': token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = cast(dict[str, str], serializer.data)
            email = data.get('email')
            password = data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response({'message': 'Login successful', 'token': token}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileview(APIView):
    renderer_classes = [CustomJSONRenderer]
    permission_classes = [IsAuthenticated]  # Allow any user to access this view
    def get(self, request, format=None):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        print("current password:", user.password)
        serializer = UserChangePasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = cast(dict[str, str], serializer.validated_data)
            current_password = data.get('old_password')
            new_password = data.get('password')
            new_password_confirm = data.get('password_confirm')
            if not user.check_password(current_password):
                return Response({'message': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)

class SendPasswordResetEmailView(APIView):
    renderer_classes = [CustomJSONRenderer]

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailViewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)
    
class UserPasswordResetView(APIView):
    renderer_classes = [CustomJSONRenderer]

    def post(self, request, uid, token, format=None):
       serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
       serializer.is_valid(raise_exception=True)
       return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)