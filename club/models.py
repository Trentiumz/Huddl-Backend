from django.db import models
from django.db.models.constraints import UniqueConstraint
from huddl.models import User
from django.core.exceptions import ValidationError

class Club(models.Model):
  owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clubs_owned', 
                            null=False, blank=False)
  name = models.CharField(max_length=255)
  description = models.TextField(max_length=1000, null=True, blank=True)
  admin = models.ManyToManyField(User, related_name='clubs_managing')
  members = models.ManyToManyField(User, related_name='clubs_in')

  join_enabled = models.BooleanField(default=False)
  join_id = models.CharField(max_length=255, blank=True, unique=True)

  def to_dict(self, include_owner=False, include_admin=False, include_members=False, 
              include_join_info=False):
    ret = {
      'id': self.id,
      'name': self.name,
      'description': self.description
    }
    if include_owner:
      ret['owner'] = self.owner.to_dict()
    if include_admin:
      ret['admin'] = [user.to_dict() for user in self.admin.all()]
    if include_members:
      ret['members'] = [user.to_dict() for user in self.members.all()]
    if include_join_info:
      ret['join_enabled'] = self.join_enabled,
      ret['join_id'] = self.join_id if self.join_enabled else None
    return ret

  def is_owner(self, user):
    return self.owner == user
  def is_admin(self, user):
    return self.is_owner(user) or self.admin.filter(id=user.id).exists()
  def is_member(self, user):
    return self.is_admin(user) or self.members.filter(id=user.id).exists()

class Activity(models.Model):
  club = models.ForeignKey(Club, on_delete=models.CASCADE, 
                           related_name='activities_planned', blank=False)
  cost = models.DecimalField(blank=False, decimal_places=2, max_digits=10)
  time = models.DurationField(blank=False)
  name = models.CharField(max_length=255, blank=False)
  description = models.TextField(blank=True, max_length=1000, default='')
  location = models.CharField(max_length=255, blank=True, null=True)
  link = models.CharField(max_length=255, blank=True, null=True)

  def to_dict(self):
    ret = {
      'club_id': self.club.id,
      'id': self.id,
      'cost': self.cost,
      'time': self.time,
      'name': self.name,
      'description': self.description
    }
    if self.link:
      ret['link'] = self.link
    if self.location:
      ret['location'] = self.location
    return ret

class ClubProfile(models.Model):
  club = models.ForeignKey(Club, on_delete=models.CASCADE, 
                           related_name='club_profiles')
  user = models.ForeignKey(User, on_delete=models.CASCADE, 
                           related_name='club_profiles')

  budget_limit = models.DecimalField(null=False, blank=False, default=0, 
                                     decimal_places=2, max_digits=10)
  maximum_time = models.DurationField(null=False, blank=False, default=0)

  class Meta:
    constraints = [models.UniqueConstraint(fields=('club', 'user'), name='unique_per_user')]

class FinalPlan(models.Model):
  club = models.ForeignKey(Club, on_delete=models.CASCADE, 
                           related_name='final_plans')
  activity = models.ForeignKey(Activity, null=True, on_delete=models.SET_NULL, related_name='plans_in')
  start_time = models.DateTimeField(null=True, blank=True)
  end_time = models.DateTimeField(null=True, blank=True)

  def clean(self):
    super().clean()
    if self.end_time is not None and self.start_time is not None:
      raise ValidationError('End time cannot be before start time')

  def to_dict(self, include_full_club_data=False):
    ret = {
      'id': self.id,
      'cost': self.activity.cost,
      'start_time': self.start_time,
      'end_time': self.end_time,
    }
    if include_full_club_data:
      ret['club'] = self.club
    else:
      ret['club'] = {
        'id': self.club.id
      }
    return ret