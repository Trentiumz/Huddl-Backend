from rest_framework.response import Response
from rest_framework import status

# Mixin to check if a user is logged in before proceeding with a request
class LoginMixin:
  def check_login(self, request):
    # If the user is not authenticated, return an unauthorized error response
    if not request.user.is_authenticated:
      return Response({"detail": "You need to be logged in"},
                      status=status.HTTP_401_UNAUTHORIZED)
    # If authenticated, return None to indicate success
    return None

  def perform_checks(self, request):
    # Wrapper method to perform the login check
    return self.check_login(request)


# Mixin to validate a serializer and return error response if invalid
class SerializerValidateMixin:
  def validate_serializer(self, serializer):
    # If the serializer is not valid, return a bad request with errors
    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # If valid, return None to indicate success
    return None

  def perform_checks(self, serializer):
    # Wrapper method to perform the serializer validation
    return self.validate_serializer(serializer)


# Combined mixin that performs both login and serializer validation checks for a specific User
class LoginAndValidateMixin(LoginMixin, SerializerValidateMixin):
  def perform_checks(self, request, serializer):
    # First check if the user is logged in
    response = self.check_login(request)
    if response:
      return response

    # Then check if the serializer is valid
    response = self.validate_serializer(serializer)
    if response:
      return response

    # If all checks pass, return None
    return None
