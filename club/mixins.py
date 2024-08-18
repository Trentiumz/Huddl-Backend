from rest_framework.response import Response
from .models import Club
from rest_framework import status

class LoginAndValidateMixin:
  def check_login(self, request):
    if not request.user.is_authenticated:
      return Response({"detail": "You need to be logged in"}, 
                      status=status.HTTP_401_UNAUTHORIZED)
    return None
  def validate_serializer(self, serializer):
    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return None
  def perform_checks(self, request, serializer):
    response = self.check_login(request)
    if response:
      return response
    response = self.validate_serializer(serializer)
    if response:
      return response
    return None


class ClubPermissionCheckMixin(LoginAndValidateMixin):
  club: None | Club = None

  def check_club_existence(self, club_id):
    club = Club.objects.filter(id=club_id).first()
    if not club:
      return Response({"detail": "There are no clubs with that id"}, 
        status=status.HTTP_404_NOT_FOUND)
    self.club = club
    return None
  def check_club_permission(self, user, allow_owner=False, 
                            allow_admin=False, allow_member=False):
    club = self.club
    assert(club is not None)
    if allow_member and club.is_member(user):
      return None
    if allow_admin and club.is_admin(user):
      return None
    if allow_owner and club.is_owner(user):
      return None
    return Response({"detail": "There are no clubs with that id"}, 
      status=status.HTTP_404_NOT_FOUND)

  def perform_checks(self, request, serializer, **kwargs):
    response = super().perform_checks(request, serializer)
    if response:
      return response

    response = self.check_club_existence(serializer.validated_data.get('id'))
    if response:
      return response

    response = self.check_club_permission(request.user, **kwargs)
    if response:
      return response

    return None