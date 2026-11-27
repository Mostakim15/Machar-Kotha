from django.urls import path, include
from accounts.views import UserChangePasswordView, UserLoginView, UserPasswordResetView, UserProfileview, UserRegistrationView,SendPasswordResetEmailView

# from accounts import views
app_name = 'accounts'
urlpatterns = [
   path('register/', UserRegistrationView.as_view(), name='register'),
   path('login/', UserLoginView.as_view(), name='login'),
   path('profile/', UserProfileview.as_view(), name='profile'),
   path('change-password/', UserChangePasswordView.as_view(), name='change-password'),
   path('send-password-reset-email/', SendPasswordResetEmailView.as_view(), name='reset-password'),
   path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password-confirm'),
   ]