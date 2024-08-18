from django.contrib.auth.backends import ModelBackend
from .models import User

class UserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        if username is None and email is None:
            raise RuntimeError('cannot authenticate without username or email')
        elif username is None:
            user = User.objects.filter(email=email).first()
        elif email is None:
            user = User.objects.filter(username=username).first()
        else:
            user = User.objects.filter(username=username, email=email).first()
        if user is None:
            return None
        if user.check_password(password):
            return user
        return None