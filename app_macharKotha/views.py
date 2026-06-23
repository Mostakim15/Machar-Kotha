from django.shortcuts import render
from rest_framework import generics
from .models import Category, Tag, Post, Comment, Bookmark
from .serializers import CategorySerializer, TagSerializer, PostSerializer, CommentSerializer, BookmarkSerializer


# Create your views here.
def home(request):
    return render(request, 'app_macharKotha/home.html')

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
