from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
#BaseUserManager is a class that provides helper methods for creating and managing user objects in Django. It is used to define custom user models and handle user creation, password hashing, and other user-related operations.

#AbstractBaseUser is a class that provides the core implementation of a user model in Django. It includes fields for authentication, such as password and last login, but does not include any additional fields like username or email. It allows developers to create custom user models by extending it and adding their own fields and methods.

# Create your models here.
class MyUserManager(BaseUserManager):
    def create_user(self, email, name, tc, password=None,password_confirm=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            tc=tc,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, tc,password=None, password_confirm=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            name=name,
            tc=tc,
            password=password,
            password_confirm=password_confirm,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=255)
    tc = models.BooleanField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    object = MyUserManager()
    objects = MyUserManager()  # This line is added to ensure that the custom user manager is used for the MyUser model.

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "tc"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin