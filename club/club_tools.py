import string
from random import choice
from .models import Club

def generate_join_id(length=24):
  cur_id = ''.join(choice(string.ascii_letters) for _ in range(length))
  while Club.objects.filter(join_id=cur_id).exists():
    cur_id = ''.join(choice(string.ascii_letters) for _ in range(length))
  return cur_id