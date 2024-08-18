from rest_framework.response import Response
from rest_framework import status

class LoginMixin:
  def check_login(self, request):
    if not request.user.is_authenticated:
      return Response({"detail": "You need to be logged in"}, 
                      status=status.HTTP_401_UNAUTHORIZED)
    return None
  def perform_checks(self, request):
    return self.check_login(request)

class SerializerValidateMixin:
  def validate_serializer(self, serializer):
    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return None
  def perform_checks(self, serializer):
    return self.validate_serializer(serializer)

class LoginAndValidateMixin:
  def perform_checks(self, request, serializer):
    response = LoginMixin().check_login(request)
    if response:
      return response
    response = SerializerValidateMixin().validate_serializer(serializer)
    if response:
      return response
    return None