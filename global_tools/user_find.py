from huddl.models import User
from django.contrib.sessions.models import Session
from django.contrib.auth.models import AnonymousUser

def update_request_user(request):
  session_id = request.data['sessionid'] if 'sessionid' in request.data else None
  if session_id:
    cur_session = Session.objects.filter(pk=session_id).first()
    if cur_session:
      request.user = User.objects.get(id=cur_session.get_decoded()['_auth_user_id'])
    else:
      request.user = AnonymousUser()
  else:
    request.user = AnonymousUser()