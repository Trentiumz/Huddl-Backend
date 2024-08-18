from django.urls import path
from .member_views import GetClubsIn, GetClub, JoinClub, LeaveClub, MyClubStatus, ViewClubProfile, EditClubProfile
from .owner_views import CreateClub, GetOwnedClubs, AdminInfo, PromoteMember, RemoveMember, DeleteClub, TransferClub, ChangeJoinStatus
from .activity_views import AddActivity, ViewActivities

urlpatterns = [
  path('create', CreateClub.as_view(), name='create_club'),
  
  path('get-owned-groups', GetOwnedClubs.as_view(), name="view_clubs_owned"),
  path('admin-group-info', AdminInfo.as_view(), name='view_club_as_admin'),
  path('get-groups-in', GetClubsIn.as_view(), name='view_clubs_in'),
  path('group-info' , GetClub.as_view(), name='view_club_info'),
  path('my-status', MyClubStatus.as_view(), name='view_my_club_status'),
  
  path('join-group', JoinClub.as_view(), name='join_club'),
  path('leave-group', LeaveClub.as_view(), name='leave_club'),

  path('promote-member', PromoteMember.as_view(), name='promote_member'),
  path('remove-member', RemoveMember.as_view(), name='remove_member'),
  path('delete-group', DeleteClub.as_view(), name='delete_club'),
  path('transfer-group', TransferClub.as_view(), name='transfer_club'),
  path('change-join-status', ChangeJoinStatus.as_view(), name='change_join_status'),

  path('add-activity', AddActivity.as_view(), name='add_activity'),
  path('view-activities', ViewActivities.as_view(), name='view_activities'),

  path('view-profile', ViewClubProfile.as_view(), name='view_club_profile'),
  path('edit-profile', EditClubProfile.as_view(), name='edit_club_profile'),
]