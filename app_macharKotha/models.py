from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# 1. Category Table
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name

# 2. Tag Table
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# 3. Post/Article Table
class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    content = models.TextField() # Rich text content for the post
    featured_image = models.ImageField(upload_to='blog_banners/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# 4. Comment Table
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies') # For Multi-level comment
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

# 5. Bookmark/Saved Post Table
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post') # Ensure a user can bookmark a post only once

    def __str__(self):
        return f"{self.user.username} bookmarked {self.post.title}"

# 6. Post View (Analytics) Table
class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField()
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"View on {self.post.title} from {self.ip_address}"

# 7. Advertisement Table
class Advertisement(models.Model):
    SLOT_CHOICES = (
        ('header', 'Header Banner'),
        ('sidebar', 'Sidebar Ad'),
        ('in_post', 'Inside Post Body'),
    )

    title = models.CharField(max_length=150)
    banner_image = models.ImageField(upload_to='ads_banners/')
    target_url = models.URLField()
    placement_slot = models.CharField(max_length=10, choices=SLOT_CHOICES, default='sidebar')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    clicks = models.PositiveIntegerField(default=0) # Click track
    impressions = models.PositiveIntegerField(default=0) # how many times the ad was shown

    def __str__(self):
        return self.title