from django.db import models
from django.db.models.constraints import UniqueConstraint
from huddl.models import User
from django.core.exceptions import ValidationError

class Club(models.Model):
  owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clubs_owned', 
                            null=False, blank=False)
  name = models.CharField(max_length=255)
  admin = models.ManyToManyField(User, related_name='clubs_managing')
  members = models.ManyToManyField(User, related_name='clubs_in')

  join_enabled = models.BooleanField(default=False)
  join_id = models.CharField(max_length=255, blank=True, unique=True)

  def to_dict(self, include_owner=False, include_admin=False, include_members=False, 
              include_join_info=False):
    ret = {
      'id': self.id,
      'name': self.name,
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
  description = models.TextField(blank=True, default='')
  link = models.CharField(max_length=255, blank=True, null=True)

  def to_dict(self):
    ret = {
      'club_id': self.club.id,
      'cost': self.cost,
      'time': self.time,
      'name': self.name,
      'description': self.description
    }
    if self.link:
      ret['link'] = self.link
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

class VotingPlan(models.Model):
  club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='voting_plan')
  cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  time = models.DurationField(null=True, blank=True)
  deadline = models.DateTimeField(null=True, blank=True)

class Vote(models.Model):
  plan = models.ForeignKey(VotingPlan, on_delete=models.CASCADE, related_name='votes')
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes_made')
  cost_min = models.DecimalField(max_digits=10, decimal_places=2, null=True)
  cost_max = models.DecimalField(max_digits=10, decimal_places=2, null=True)
  time = models.DurationField(null=True, blank=True)
  
  class Meta:
    constraints = [
      UniqueConstraint(fields=('plan', 'user'), name='one-vote-per-user')
    ]

class FinalPlan(models.Model):
  club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='final_plan')
  activity = models.ForeignKey(Activity, null=True, on_delete=models.SET_NULL, related_name='plans_in')
  start_time = models.DateTimeField(null=True, blank=True)
  end_time = models.DateTimeField(null=True, blank=True)
  
  class Meta:
    constraints = [
      UniqueConstraint(fields=['club'], name='one-plan-per-club')
    ]