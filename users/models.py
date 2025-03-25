from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from datetime import timedelta


class ExpiryTime:
    """Handles expiry time calculations."""

    def __init__(self, minutes=10):
        self.minutes = minutes
        self.expiry_time = self.calculate()

    def calculate(self):
        """Calculates the expiry time."""
        return now() + timedelta(minutes=self.minutes)

    @staticmethod
    def is_expired(expiry_time):
        """Checks if the confirmation code has expired."""
        return now() > expiry_time


class User(AbstractUser):
    is_active = models.BooleanField(default=True)


class UserConfirmation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="confirmation")
    code = models.CharField(max_length=6, default='000000')  # Static default value
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField(default=now)  # Default to current timestamp

    def regenerate_code(self):
        """Resets expiry time."""
        self.expiry_time = ExpiryTime().calculate()
        self.save()

    def is_expired(self):
        """Checks if the confirmation code has expired."""
        return ExpiryTime.is_expired(self.expiry_time)
