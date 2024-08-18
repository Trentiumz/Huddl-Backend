from .models import Club, Activity
from .mixins import LoginAndValidateMixin, ClubPermissionCheckMixin
from global_tools.user_find import update_request_user
from rest_framework.views import APIView
from rest_framework import status, serializers
from rest_framework.response import Response

class AddActivitySerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)
  cost = serializers.DecimalField(required=False, decimal_places=2, max_digits=10)
  time = serializers.DurationField(required=True)
  name = serializers.CharField(max_length=255, required=True)
  description = serializers.CharField(max_length=32768, required=False)
  link = serializers.CharField(max_length=255, required=False)
class AddActivity(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = AddActivitySerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True, allow_admin=True, allow_member=True)
    if response:
      return response
    club = self.club
    data = serializer.validated_data
    activity = Activity.objects.create(club=club, cost=data.get('cost'), time=data.get('time'), name=data.get('name'))
    if data.get('description'):
      activity.description = data.get('description')
    if data.get('link'):
      activity.link = data.get('link')
    activity.save()
    return Response({"detail": "activity added"}, status=status.HTTP_201_CREATED)

class ActivityViewSerializer(serializers.Serializer):
  id = serializers.IntegerField(required=True)
class ViewActivities(ClubPermissionCheckMixin, APIView):
  def post(self, request, *args, **kwargs):
    update_request_user(request)
    serializer = ActivityViewSerializer(data=request.data)
    response = self.perform_checks(request, serializer, allow_owner=True, allow_admin=True, allow_member=True)
    if response:
      return response

    club = self.club
    activities = club.activities_planned.all()
    return Response([activity.to_dict() for activity in activities], 
                    status=status.HTTP_200_OK)