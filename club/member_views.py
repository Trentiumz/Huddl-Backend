from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from .models import Club, ClubProfile
from .mixins import LoginAndValidateMixin, ClubPermissionCheckMixin
from global_tools.user_find import update_request_user

class ClubsInSerializer(serializers.Serializer):
  detailed = serializers.BooleanField(required=False, default=False)
class GetClubsIn(LoginAndValidateMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = ClubsInSerializer(data=request.data)
    response = self.perform_checks(request, serializer)
    if response:
      return response
    validated_data = serializer.validated_data
    is_detailed = validated_data.get('detailed')
    clubs = request.user.clubs_in.all()
    info = [club.to_dict(include_owner=is_detailed, include_admin=is_detailed, 
                         include_members=is_detailed) for club in clubs]
    return Response({"clubs": info}, status=status.HTTP_200_OK)

class GetClubSerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)
  detailed = serializers.BooleanField(default=False)
class GetClub(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = GetClubSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True, 
                                   allow_admin=True, allow_member=True)
    if response:
      return response
    data = serializer.validated_data
    club = self.club
    detailed = data.get('detailed')
    return Response(club.to_dict(include_owner=detailed, include_admin=detailed, 
                                 include_members=detailed), status=status.HTTP_200_OK)

class JoinClubSerializer(serializers.Serializer):
  join_id = serializers.CharField(required=True, max_length=255, allow_blank=False)
class JoinClub(LoginAndValidateMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = JoinClubSerializer(data=request.data)
    response = self.perform_checks(request, serializer)
    if response:
      return response
      
    validated_data = serializer.validated_data
    join_id = validated_data.get('join_id')
    valid_clubs = Club.objects.filter(join_enabled=True, join_id=join_id)
    if not valid_clubs.exists():
      return Response({"detail": "invalid join id"}, status=status.HTTP_404_NOT_FOUND)
    club = valid_clubs.first()
    club.members.add(request.user)

    club.save()

class ClubLeaveSerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)
class LeaveClub(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = JoinClubSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True, 
                                   allow_admin=True, allow_member=True)
    if response:
      return response

    club = self.club
    if club.owner == request.user:
      return Response({"detail": "the owner cannot leave the club - delete the club instead"},
                      status=status.HTTP_400_BAD_REQUEST)
    club.members.remove(request.user)
    club.admin.remove(request.user)
    club.save()
    return Response({"detail": "left the club"}, status=status.HTTP_200_OK)

class MyStatusSerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)
class MyClubStatus(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = MyStatusSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True,
                                   allow_admin=True, allow_member=True)
    if response:
      return response

    club = self.club
    user_status = {
      'member': club.members.filter(email=request.user.email).exists(),
      'admin': club.admin.filter(email=request.user.email).exists(),
      'owner': club.owner == request.user
    }
    return Response(user_status, status=status.HTTP_200_OK)

def get_profile(club, user):
  profile = club.club_profiles.filter(user=user).first()
  if profile is None:
    profile = ClubProfile.objects.add(user=user, club=club, 
                                      budget_limit=user.default_budget_limit, 
                                      maximum_time=user.default_max_time)
    profile.save()
  return profile

class ViewClubProfileSerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)
class ViewClubProfile(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = ViewClubProfileSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True, allow_admin=True, allow_member=True)
    if response:
      return response

    return Response(get_profile(self.club, request.user).to_dict(),
                    status=status.HTTP_200_OK)

class EditClubProfileSerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)
  budget_limit = serializers.DecimalField(required=False, decimal_places=2, 
                                          max_digits=10)
  maximum_time = serializers.DurationField(required=False)
class EditClubProfile(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = ViewClubProfileSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True, allow_admin=True, allow_member=True)
    if response:
      return response

    profile = get_profile(self.club, request.user)
    data = serializer.validated_data
    if data.get('budget_limit'):
      profile.budget_limit = data.get('budget_limit')
    if data.get('maximum_time'):
      profile.maximum_time = data.get('maximum_time')
    profile.save()
    return Response({"details": "saved profile"}, status=status.HTTP_200_OK)

class GetPlanSerializer(serializers.Serializers):
  id = serializers.IntegerField(required=True)
class GetPlans(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = GetPlanSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True, allow_admin=True, allow_member=True)
    if response:
      return response

    club = self.club
    plans = club.final_plans.all()
    return Response([plan.to_dict() for plan in plans], status=status.HTTP_200_OK)