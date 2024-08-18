from django.core.exceptions import ValidationError
from django.contrib.sessions.models import Session
from django.shortcuts import render
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import password_validation
from .models import User
from .mixins import LoginAndValidateMixin
from global_tools.user_find import update_request_user


class LoginSerializer(serializers.Serializer):
  email = serializers.EmailField(required=True)
  password = serializers.CharField(required=True)


# Create your views here.
class Login(APIView):

  def post(self, request, *args, **kwargs):
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
      validated_data = serializer.validated_data

      if validated_data:
        email = validated_data.get('email')
        password = validated_data.get('password')
        user = authenticate(email=email, password=password)

        if user is not None:
          login(request, user)
          session_id = request.session.session_key
          response = Response(
              {
                  "detail": "Login Successful",
                  "session_id": session_id
              },
              status=status.HTTP_200_OK)
          return response
        else:
          return Response({"detail": "Credentials Invalid"},
                          status=status.HTTP_401_UNAUTHORIZED)
      else:
        raise RuntimeError("validated data shouldn't be empty")
    else:
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BasicRegistrationSerializer(serializers.Serializer):
  username = serializers.CharField(max_length=255, required=True)
  email = serializers.EmailField(max_length=255, required=True)
  full_name = serializers.CharField(max_length=255, required=True)
  password = serializers.CharField(required=True)
  default_budget_limit = serializers.DecimalField(required=False, decimal_places=2,
                                             max_digits=10)
  default_max_time = serializers.DurationField(required=False)

  def validate_username(self, value):
    if User.objects.filter(username=value).exists():
      raise ValidationError("Username already exists")
    return value

  def validate_email(self, value):
    if User.objects.filter(email=value).exists():
      raise ValidationError("Email already exists")
    return value

  def validate_password(self, value):
    try:
      password_validation.validate_password(value)
    except ValidationError as e:
      raise e
    return value

class Register(APIView):
  def post(self, request, *args, **kwargs):
    serializer = BasicRegistrationSerializer(data=request.data)
    if serializer.is_valid():
      validated_data = serializer.validated_data
      if validated_data:
        username = validated_data.get('username')
        email = validated_data.get('email')
        full_name = validated_data.get('full_name')
        password = validated_data.get('password')
        user = User.objects.create_user(username=username,
                                        email=email,
                                        full_name=full_name,
                                        password=password)
        if validated_data.get('default_budget_limit'):
          user.default_budget_limit = validated_data.get('default_budget_limit')
        if validated_data.get('default_max_time'):
          user.default_max_time = validated_data.get('default_max_time')
        user.save()
        login(request, user)
        session_id = request.session.session_key
        response = Response(
            {
                "detail": "User Created",
                "session_id": session_id
            },
            status=status.HTTP_201_CREATED)
        return response
      else:
        raise RuntimeError("validated data shouldn't be empty")
    else:
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Logout(APIView):
  def post(self, request):
    update_request_user(request)
    if request.user.is_authenticated:
      Session.objects.filter(pk=request.data['sessionid']).delete()
      return Response({"detail": "logged out"}, status=status.HTTP_200_OK)
    else:
      return Response({"detail": "not logged in"}, status=status.HTTP_202_ACCEPTED)


class MyInfo(APIView):

  def post(self, request, *args, **kwargs):
    update_request_user(request)
    if request.user.is_authenticated:
      return Response(request.user.to_dict(clubs_owned=True,
                                           clubs_managing=True,
                                           clubs_in=True),
                      status=status.HTTP_200_OK)
    else:
      return Response({"detail": "not logged in"},
                      status=status.HTTP_400_BAD_REQUEST)


class UpdateInfoSerializer(serializers.Serializer):
  username = serializers.CharField(max_length=255, required=False)
  full_name = serializers.CharField(max_length=255, required=False)
  old_password = serializers.CharField(max_length=255, required=False)
  new_password = serializers.CharField(max_length=255, required=False)
  default_budget_limit = serializers.DecimalField(required=False, 
                          decimal_places=2, max_digits=10)
  default_max_time = serializers.DurationField(required=False)

  def validate_username(self, value):
    if User.objects.filter(username=value).exists():
      raise ValidationError("Username already exists")
    return value

  def validate_old_password(self, value):
    if not self.context.get('user').check_password(value):
      raise ValidationError("Old Password is incorrect")
    return value

  def validate_new_password(self, value):
    try:
      password_validation.validate_password(value)
    except ValidationError as e:
      raise e
    return value

  def validate(self, data):
    if not self.context.get('user').is_authenticated:
      raise ValidationError("not logged in")
    return super().validate(data)


class UpdateInfo(LoginAndValidateMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = UpdateInfoSerializer(data=request.data,
                                      context={'user': request.user})
    response = self.perform_checks(request, serializer)
    if response:
      return response

    data = serializer.validated_data
    if data.get('new_password') and not request.user.check_password(
        data.get('old_password')):
      return Response({"detail": "old password is incorrect"},
                      status=status.HTTP_400_BAD_REQUEST)

    if data.get('username'):
      request.user.username = data.get('username')
    if data.get('full_name'):
      request.user.full_name = data.get('full_name')
    if data.get('new_password'):
      request.user.set_password(data.get('new_password'))
    if data.get('default_budget_limit'):
      request.user.default_budget_limit = data.get('default_budget_limit')
    if data.get('default_max_time'):
      request.user.default_max_time = data.get('default_max_time')
    request.user.save()
    return Response({"detail": "user updated"}, status=status.HTTP_200_OK)


class SignedIn(APIView):

  def post(self, request, *args, **kwargs):
    update_request_user(request)
    return Response({"signed-in": request.user.is_authenticated},
                    status=status.HTTP_200_OK)
