from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from .models import Club, FinalPlan, Activity
from .club_tools import generate_join_id
from .mixins import LoginAndValidateMixin, ClubPermissionCheckMixin
from global_tools.user_find import update_request_user

class ClubIDSerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)

class ClubCreateSerializer(serializers.Serializer):
  name = serializers.CharField(max_length=255, required=True)
  description = serializers.CharField(max_length=1000, required=False)
  join_enabled = serializers.BooleanField(required=False)
class CreateClub(LoginAndValidateMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = ClubCreateSerializer(data=request.data)
    response = self.perform_checks(request, serializer)
    if response:
      return response
    validated_data = serializer.validated_data
    name = validated_data.get('name')
    join_enabled = validated_data.get('join_enabled')
    join_id = ""
    if join_enabled:
      join_id = generate_join_id()
    club = Club.objects.create(name=name, join_enabled=join_enabled,
                               join_id=join_id,owner=request.user)
    if validated_data.get('description'):
      club.description = validated_data.get('description')
    club.admin.add(request.user)
    club.members.add(request.user)
    club.save()
    return Response({"detail": "created club", "club_id": club.id}, 
                    status=status.HTTP_201_CREATED)

class OwnedClubSerializer(serializers.Serializer):
  detailed = serializers.BooleanField(required=False, default=False)
class GetOwnedClubs(LoginAndValidateMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = OwnedClubSerializer(data=request.data)
    response = self.perform_checks(request, serializer)
    if response:
      return response

    validated_data = serializer.validated_data
    is_detailed = validated_data.get('detailed')
    clubs = request.user.clubs_owned.all()
    info = [club.to_dict(include_owner=is_detailed, include_admin=is_detailed, 
                         include_members=is_detailed) for club in clubs]
    return Response({"clubs": info}, status=status.HTTP_200_OK)

class AdminInfoSerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)
  detailed = serializers.BooleanField(default=False)
class AdminInfo(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = AdminInfoSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True, allow_admin=True)
    if response:
      return response

    data = serializer.validated_data
    club = self.club
    detailed = data.get('detailed')
    return Response(club.to_dict(include_owner=detailed, include_admin=detailed, 
       include_members=detailed, include_join_info=True), status=status.HTTP_200_OK)

class MemberPromotionSerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)
  promote_email = serializers.EmailField(required=True, max_length=255)
class PromoteMember(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = MemberPromotionSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True)
    if response:
      return response

    data = serializer.validated_data
    club = self.club
    to_promote_email = data.get('promote_email')
    promote_user = club.members.filter(email=to_promote_email)
    if club.admin.filter(email=to_promote_email).exists():
      return Response({"detail": "cannot promote an admin"}, status=status.HTTP_400_BAD_REQUEST)
    if not promote_user.exists():
      return Response({"detail": "the user does not exist in this group"}, 
                      status=status.HTTP_400_BAD_REQUEST)
    club.admin.add(promote_user[0])
    club.save()
    return Response({"detail": "made user an admin"}, status=status.HTTP_200_OK)

class MemberRemovalSerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)
  remove_email = serializers.CharField(required=True, max_length=255)
class RemoveMember(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = MemberRemovalSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True)
    if response:
      return response

    data = serializer.validated_data
    club = self.club
    to_remove_email = data.get('remove_email')
    if to_remove_email == club.owner.email:
      return Response({"detail": "owner cannot be removed"}, status=status.HTTP_400_BAD_REQUEST)
    if to_remove_email == request.user.email:
      return Response({"detail": "you cannot remove yourself"},
                      status=status.HTTP_400_BAD_REQUEST)
    club.admin.remove(club.admin.filter(email=to_remove_email).first())
    club.members.remove(club.members.filter(email=to_remove_email).first())
    club.save()
    return Response({"detail": "user removed"}, status=status.HTTP_200_OK)

class DeleteClub(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = ClubIDSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True)
    if response:
      return response

    club = self.club
    club.delete()

class TransferOwnerSerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)
  new_owner_email = serializers.CharField(required=True, max_length=255)
class TransferClub(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = TransferOwnerSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True)
    if response:
      return response

    data = serializer.validated_data
    club = self.club
    new_owner_email = data.get('new_owner_email')
    if new_owner_email == club.owner.email:
      return Response({"detail": "cannot transfer ownership to yourself"}, 
                      status=status.HTTP_400_BAD_REQUEST)
    new_owner = club.members.filter(email=new_owner_email).first()
    if new_owner is None:
      new_owner = club.admin.filter(email=new_owner_email).first()
      
    club.members.add(new_owner)
    club.admin.add(new_owner)
    club.owner = new_owner
    club.save()
    return Response({"detail": "club ownership transferred"}, status=status.HTTP_200_OK)

class ChangeJoinSerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)
  join_enabled = serializers.BooleanField(required=True)
class ChangeJoinStatus(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = ChangeJoinSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True)
    if response:
      return response

    club = self.club
    data = serializer.validated_data
    if data.get('join_enabled'):
      club.join_enabled = True
      club.join_id = generate_join_id()
      club.save()
      return Response({"detail": "club joining enabled", "join_id": club.join_id},
                     status=status.HTTP_200_OK)
    else:
      club.join_enabled = False
      club.join_id = ""
      club.save()
      return Response({"detail": "club joining disabled"},
                      status=status.HTTP_200_OK)

class CreateFinalPlanSerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)
  activity_id = serializers.IntegerField(required=True)
  start_time = serializers.DateTimeField(required=True)
  end_time = serializers.DateTimeField(required=True)

  def validate(self, data):
    if data['end_time'] < data['start_time']:
      raise serializers.ValidationError("End time cannot be before start time")
    super().validate(data)
    return data
class CreateFinalPlan(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = CreateFinalPlanSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True, allow_admin=True)
    if response:
      return response

    club = self.club
    data = serializer.validated_data

    if not club.activities_planned.filter(id=data.get('activity_id')).exists():
      return Response({"detail": "activity not found"},
                      status=status.HTTP_404_NOT_FOUND)
    
    activity = Activity.objects.get(id=data.get('activity_id'))
    final_plan = FinalPlan.objects.create(club=club, activity=activity, start_time=data.get('start_time'), end_time=data.get('end_time'))
    return Response({"detail": "final plan created", "id": final_plan.id}, status=status.HTTP_201_CREATED)

class DeleteFinalPlanSerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)
  plan_id = serializers.IntegerField(required=True)

class DeleteFinalPlan(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = DeleteFinalPlanSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True, allow_admin=True)
    if response:
      return response

    club = self.club
    data = serializer.validated_data
    if not club.final_plans.filter(id=data.get('plan_id')).exists():
      return Response({"detail": "plan does not exist"},
                      status=status.HTTP_404_NOT_FOUND)
    
    plan = Club.final_plans.get(id=data.get('plan_id'))
    plan.delete()
    return Response({"detail": "final plan deleted",}, 
                    status=status.HTTP_200_OK)

class EditFinalPlanSerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)
  plan_id = serializers.IntegerField(required=True)
  activity_id = serializers.IntegerField(required=False)
  start_time = serializers.DateTimeField(required=False)
  end_time = serializers.DateTimeField(required=False)
class EditFinalPlan(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = EditFinalPlanSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True, allow_admin=True)
    if response:
      return response

    club = self.club
    data = serializer.validated_data
    if not club.final_plans.filter(id=data.get('plan_id')).exists():
      return Response({"detail": "plan does not exist"},
        status=status.HTTP_404_NOT_FOUND)
    
    plan = club.final_plans.get(id=data.get('plan_id'))
    if data.get('activity_id'):
      if not club.activities_planned.filter(id=data.get('activity_id')).exists():
        return Response({"detail": "activity does not exist"},
          status=status.HTTP_404_NOT_FOUND)
      plan.activity = Club.activities_planned.get(id=data.get('activity_id'))
    if data.get('start_time'):
      if data.get('end_time') and data.get('end_time') < data.get('start_time') or data.get('end_time') is None and plan.end_time is not None and plan.end_time < data.get('start_time'):
        return Response({"detail": "end time cannot be before start time"}, 
                        status=status.HTTP_400_BAD_REQUEST)
      plan.start_time = data.get('start_time')
    if data.get('end_time'):
      if data.get('start_time') and data.get('start_time') > data.get('end_time') or data.get('start_time') is None and plan.start_time is not None and plan.start_time > data.get('end_time'):
        return Response({"detail": "start time cannot be after end time"},  
                        status=status.HTTP_400_BAD_REQUEST)
      plan.end_time = data.get('end_time')
    plan.save()
    return Response({"detail": "plan updated"}, status=status.HTTP_201_CREATED)