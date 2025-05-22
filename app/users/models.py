from django.db import models
from django.urls import reverse
# Create your models here.

class User(models.Model):
    gender = models.CharField(max_length=10)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=False)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    picture = models.URLField()
    
    def get_more_info(self):
        return reverse('users:user_detail', kwargs={'user_id': self.id})

    def __str__(self):
        return reverse('users:user_detail', kwargs={'user_id': self.id})