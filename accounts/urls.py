from django.urls import path, include
from accounts.views import UserLoginView, UserRegistrationView

# from accounts import views
app_name = 'accounts'
urlpatterns = [
   path('register/', UserRegistrationView.as_view(), name='register'),
   path('login/', UserLoginView.as_view(), name='login'),
   ]