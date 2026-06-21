Here is the exact code block containing the entire unified page as a single `README.md` file:

```markdown
# Machar-Kotha

A feature-rich, scalable Blog Website built with the Django web framework.

---

## 📝 Overview

**Machar-Kotha** is a modular blog application that demonstrates structured Django database design. Moving beyond basic CRUD features, it incorporates robust relational models for taxonomy mapping, nested user engagement, analytical traffic auditing, bookmarking systems, and scheduled advertisement engines.

---

## ✨ Features

- **Content Management:** Multi-status workflows (`Draft`, `Scheduled`, `Published`) tied with dynamic Categories and Tags.
- **Nested Commenting:** Multi-level, infinite thread discussion mechanics using self-referential relations.
- **Personalization:** Secure user reading lists with strict database-level duplication guards.
- **Analytics Engine:** Silent post impression tracking using client system IP addresses.
- **Ad Delivery System:** Asset slots (`Header`, `Sidebar`, `In-Post`) managing click metrics and runtime lifespans.

---

## 🗄️ Database Architecture
```

```
[User] <─── (Auth, Authorship, Interactivity)
  │
  ├───► [Post] ◄─── (Many-to-Many) ───► [Tag]
  │       │
  │       ├───► [Category] (Foreign Key Relation)
  │       ├───► [PostView] (IP & Traffic Analytics Tracker)
  │       └───► [Comment]  (Self-Referential Nested Tree)
  │
  └───► [Bookmark] (Unique Composite Constraint Connection)

[Advertisement] ─── (Isolated Dynamic Scheduling Engine)

```

````

---

## 🚀 Quick Start & Installation

### 1. Environment & Dependencies
Clone the repository and initialize your Python virtual environment:
```bash
git clone [https://github.com/yourusername/machar-kotha.git](https://github.com/yourusername/machar-kotha.git) && cd machar-kotha
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install django pillow

````

### 2. Migration & Superuser Initialization

Sync database schemas and generate an administrative user to manage layout models:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

```

### 3. Execution

Launch the local application staging server:

```bash
python manage.py runserver

```

- **Client Interface:** Open `http://127.0.0.1:8000/` to browse content.
- **Admin Dashboard:** Open `http://127.0.0.1:8000/admin/` to manage blogs, review metrics, and control advertisement layouts.

---

Below is the foundational database implementation schema powering this application:

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# 1. Category Table
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
    content = models.TextField()
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
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
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
        unique_together = ('user', 'post')

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
    clicks = models.PositiveIntegerField(default=0)
    impressions = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

```

---

## 📌 Implementation Notes

- **Media Handling:** Ensure `MEDIA_URL` and `MEDIA_ROOT` are configured within your project variables to allow the upload of blog images and advertisement banner headers.
- **Data Integrity:** The application implements strict `unique_together` meta-constraints to systematically reject redundant database entries for bookmark instances.

```

```
