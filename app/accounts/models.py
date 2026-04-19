from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    ROLE_CHOICES = [("buyer", "Buyer"),("seller", "Seller"),("admin", "Admin"),]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="buyer")
    is_approved = models.BooleanField(default=False) #added this in so admins can approve or deny accounts- madee

#adding in accessibility settings for users-madee
class UserPreference(models.Model):
    THEME_CHOICES = [("light", "Light"), ("dark", "Dark"), ("high_contrast", "High Contrast"), ("inverted", "Inverted"),]

    TEXT_SIZE_CHOICES = [("normal", "Normal"), ("large", "Large"), ("xlarge", "Extra Large"),]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="preferences")
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default="light")
    text_size = models.CharField(max_length=20, choices=TEXT_SIZE_CHOICES, default="normal")
    reduce_motion = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)