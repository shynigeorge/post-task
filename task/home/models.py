from django.utils import timezone

from django.contrib.auth.models import AbstractUser
from django.db import models



class CustomUser(AbstractUser):
    name=models.CharField(max_length=200)
    phone_no=models.CharField(max_length=10)
    def __str__(self):
        return self.name



class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # The user who created the post
    title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.ManyToManyField(CustomUser, related_name='tagged_posts')
    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.title

class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    liked = models.BooleanField(default=False)  # True if liked, False if unliked

    class Meta:
        unique_together = ('user', 'post')  # Ensures a user can only have one like/unlike per post

    def __str__(self):
        return f"{self.user} {'liked' if self.liked else 'unliked'} {self.post.title}"