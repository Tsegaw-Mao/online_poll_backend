from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Custom User model for authentication (extends Django's AbstractUser)."""
    pass


class Poll(models.Model):
    """Poll model with expiry date and creator."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="polls", default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        """A poll is active if it has no expiry or if expiry is in the future."""
        return self.expiry_date is None or self.expiry_date > timezone.now()


class Option(models.Model):
    """Options for each poll."""
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)
    vote_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.text} ({self.vote_count} votes)"


class Vote(models.Model):
    """Each user can vote once per poll."""
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("poll", "user")  # prevent duplicate votes
