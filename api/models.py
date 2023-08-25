from django.db import models
import string
import random

# Create your models here.
#standard database models are created here which is instead of a table
#for this project we are creating a model for users as we collect all 
# users to control the music over a host music
#generation of a random 6 digit code for the persons to join
def generateuniquiecode():
    length = 6
    
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        if Room.objects.filter(code=code).count() == 0:
            break
    
    return code

class Room(models.Model):
    code=models.CharField(max_length = 8, default = generateuniquiecode, unique = True)
    host=models.CharField(max_length= 50,unique=True)
    guest_can_pause = models.BooleanField( null = False, default = False)
    votes_to_skip = models.IntegerField( null = False, default = 1)
    created_at = models.DateTimeField(auto_now_add = True)
    current_song=models.CharField(max_length=50, null=True)