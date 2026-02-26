from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ("buyer", "Buyer"),
        ("seller", "Seller"),
        ("admin", "Admin"),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="buyer")

    ACCOUNT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    account_status = models.CharField(
        max_length=10,
        choices=ACCOUNT_STATUS_CHOICES,
        default="Pending"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"