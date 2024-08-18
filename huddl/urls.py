from django.urls import path
from .views import Login, Register, Logout, MyInfo, UpdateInfo, SignedIn

urlpatterns = [
  path('login', Login.as_view(), name='login'),
  path('register', Register.as_view(), name='register'),
  path('logout', Logout.as_view(), name='logout'),
  path('my-info', MyInfo.as_view(), name='my_info'),
  path('update-info', UpdateInfo.as_view(), name='update_info'),
  path('signed-in', SignedIn.as_view(), name='signed_in')
]