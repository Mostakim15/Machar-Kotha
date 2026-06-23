from django.contrib import admin
from .models import Category, Tag, Post, Comment, Bookmark, Advertisement, PostView

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'published_at', 'created_at', 'updated_at')
    list_filter = ('status', 'category', 'tags', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ('status', 'published_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'parent', 'content', 'created_at')
    list_filter = ('post', 'user')
    search_fields = ('content',)
    date_hierarchy = 'created_at'
    ordering = ('created_at',)

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('user', 'post')
    date_hierarchy = 'created_at'
    ordering = ('created_at',)



@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ('post','viewed_at','ip_address')
    list_filter = ('post', 'viewed_at')
    date_hierarchy = 'viewed_at'
    ordering = ('viewed_at',)

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'banner_image',
        'target_url',
        'placement_slot',
        'start_date',
        'end_date',
        'is_active'
    )

    search_fields = ('title', 'target_url')
    list_filter = ('placement_slot', 'is_active')
    date_hierarchy = 'start_date'
    ordering = ('start_date',)