from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from datetime import timedelta

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255)
    is_staff = models.BooleanField()
    password = models.CharField(blank=True, max_length=255)

    default_budget_limit = models.DecimalField(default=50, decimal_places=2,
                                               max_digits=10)
    default_max_time = models.DurationField(default=timedelta(hours=2))

    REQUIRED_FIELDS = ['email', 'full_name']

    def to_dict(self, clubs_owned=False, clubs_managing=False, clubs_in=False):
        ret = {
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_staff': self.is_staff,
            'default_budget_limit': self.default_budget_limit,
            'default_max_time': self.default_max_time
        }
        if clubs_owned:
            ret['groups_owned'] = [club.to_dict() for club in self.clubs_owned.all()]
        if clubs_managing:
            ret['groups_managed'] = [club.to_dict() for club in self.clubs_managing.all()]
        if clubs_in:
            ret['groups_in'] = [club.to_dict() for club in self.clubs_in.all()]
        return ret

class UserManager(BaseUserManager):
    def create_user(self, username, full_name, email, password=None, 
                    is_staff=False, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, full_name=full_name, 
                          password=password, is_staff=is_staff, **extra_fields)
        user.save()
        return user
    def create_superuser(self, username, full_name, email, 
                         password=None, **extra_fields):
        return self.create_user(username, full_name, email, password=password, 
                                is_staff=True, **extra_fields)