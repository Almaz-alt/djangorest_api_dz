import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from datetime import timedelta


def generate_code():
    """Generate a 6-digit random code."""
    return f"{random.randint(100000, 999999):06}"


def calculate_expiry_time():
    """Calculate expiry time for the confirmation code."""
    return now() + timedelta(minutes=10)


class User(AbstractUser):
    is_active = models.BooleanField(default=True)


class UserConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="confirmation")
    code = models.CharField(
        max_length=6,
        default=generate_code
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField(default=calculate_expiry_time)

    def is_expired(self):
        """Check if the confirmation code is expired."""
        return now() > self.expiry_time
