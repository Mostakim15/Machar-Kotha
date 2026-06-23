from django.urls import path, include
from . import views

app_name = 'app_macharKotha'

urlpatterns = [
    path('', views.home, name='home'),
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
]