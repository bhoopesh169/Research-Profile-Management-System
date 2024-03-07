from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default=True)
    department = models.CharField(max_length=100, default=True)
    position = models.CharField(max_length=100, default=True)
    education = models.CharField(max_length=100, default=True)
    email = models.EmailField(unique=True, default=True)
    research_interests = models.CharField(max_length=255, default=True)
    profile_photo = models.ImageField(upload_to='profile_photo/', blank=True, null=True)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user}'
    
class contact_info(models.Model):
    u_email = models.EmailField()
    u_message = models.CharField(max_length=200)
    
    def __str__(self):
        return self.u_email

class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}'