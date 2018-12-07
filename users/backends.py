from django.conf import settings
from users.models import CustomUser

class SpotifyAuthBackEnd:    
    def authenticate(self, request, spotifyid=None):
        try:
            
            user  =CustomUser.objects.filter( spotifyid__contains=spotifyid ).first()#= CustomUser.objects.get(spotifyid= str(spotifyid))
            print(user)
            if user:
                return user
        except CustomUser.DoesNotExist:
            return None 
    
    def get_user(self, pk=None):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return None