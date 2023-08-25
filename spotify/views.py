from django.shortcuts import render, redirect
from .credentials import REDIRECT_URI, CLIENT_SECRET, CLIENT_ID
from rest_framework.views import APIView
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from .util import *
from api.models import Room
from .models import Vote

# THIS IS USED FOR THE REQUESTING AUTHORIZATION TO ACCESS DATA.
class AuthURL(APIView):
    def get(self,request,format=None):
        scopes= 'user-read-playback-state user-modify-playback-state user-read-currently-playing'
        #this is the information that we want to access from the WEB API
        # url-dataype=string
        url= Request("GET", "https://accounts.spotify.com/authorize", params = {
            'scope' : scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
            }).prepare().url
        
        return Response({'url':url}, status=status.HTTP_202_ACCEPTED)
        # params are client id, response type, redirect uri, state(x) and scope.
        # aFTER autherization from the webapi we get the code and the status from it as the response, and we need to 
        # store these code in view or a function that takes the code and do something with it

# after the request is sent, it gives the response to this callback function, so after that we 
# send the request using the "code" to get the access to the access token etc. 
def spotify_callback(request,format=None):
    code=request.GET.get('code')
    error=request.GET.get('error')
    print("Nastyyyyyyyyyyyyy")
    response= post("https://accounts.spotify.com/api/token", data = {
   
        'grant_type':'authorization_code',
        'code' : code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()
    print(response)
    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')
    print(request.session.session_key, access_token, token_type, expires_in,refresh_token)
    # everytime a user is joined in the room using the code, user need to authenticate
    # with the spotify using tokens and there will no. of tokens that we will have to store these in the database.
    # access token is generated only for the host of the room.
    if not request.session.exists(request.session.session_key):
        request.session.create()
    
    update_or_create_user_tokens(request.session.session_key, access_token, token_type, expires_in,refresh_token)
    return redirect('frontend:')
# end-pint we will hit where it will lwt us know whether we are authenticated or not.

class IsAuthenticated(APIView):
    def get(self, request, format=None):
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)
    

class CurrentSong(APIView):
    def get(self,request,format=None):
        room_code=self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        
        print(room.host)
        host = room.host
        endpoint = "player/currently-playing"
        response= execute_spotify_api_request(host, endpoint)
        print("type of response is: ", type(response))
        if (type(response) == dict and (('Error' in response) or ('item' not in response))):
            return Response({},status=status.HTTP_204_NO_CONTENT)
        elif(type(response) == dict):
            try:
                item = response.get('item')
                progress = response.get('progress_ms')
                is_playing = response.get('is_playing')
                duration = response.get('duration_ms')
                album_cover = item.get("album").get('images')[0].get('url')
                song_id = item.get('id')
                for i,artist in enumerate(item.get('artists')):
                    if i>0:
                        artist_name += ', '
                        name=artist.get('name')
                        artist_string+=name
                votes = len(Vote.objects.filter(room=room, song_id=song_id))
                song = {
                    'title': item.get('name'),
                    'artist': artist_string,
                    'duration': duration,
                    'time': progress,
                    'image_url': album_cover,
                    'is_playing': is_playing,
                    'votes': votes,
                    'votes_required': room.votes_to_skip,
                    'id': song_id
                }
                self.update_room_song(room,song_id)
                
                return Response(song, status=status.HTTP_200_OK)
            except KeyError as e:
                print('I got a KeyError - reason "%s"' % str(e))
    
    def update_room_song(self, room, song_id):
        current_song = room.current_song

        if current_song != song_id:
            room.current_song = song_id
            room.save(update_fields=['current_song'])
            votes = Vote.objects.filter(room=room).delete()


class PauseSong(APIView):
    def put(self,response,format=None):
        room_code = self.request.session.get('room_code')
        room= Room.objects.filter(code=room_code)
        if room.exists() :
            room = room[0]
        # check if the guests are allowed to play or pause the song.
        if self.request.session.session_key==room.host or room.guest_can_pause:
           pause_song(room.host)
           return Response({},status=status.HTTP_204_NO_CONTENT) 
        return Response({},status=status.HTTP_403_FORBIDDEN)
        
class PlaySong(APIView):
    def put(self,response,format=None):
        room_code = self.request.session.get('room_code')
        room= Room.objects.filter(code=room_code)
        if room.exists() :
            room = room[0]
        # check if the guests are allowed to play or pause the song.
        if self.request.session.session_key==room.host or room.guest_can_pause:
           play_song(room.host)
           return Response({},status=status.HTTP_204_NO_CONTENT) 
        return Response({},status=status.HTTP_403_FORBIDDEN)

class SkipSong(APIView):
    def post(self,request, format=None):
        room_code = self.request.get('room_code')
        room = Room.objects.filter(code=room_code)
        votes=Vote.objects.filter(room=room, song_id= room.current_song)
        votes_needed=room.votes_to_skip
        
        if self.request.session.session_key==room.host or len(votes)+1 >= votes_needed:
            votes.delete()
            skip_song(room.host)
        else:
            vote = Vote(user=self.request.session.session_key, room=room, song_id=room.current_song)
            vote.save()
          
        return Response({}, status = status.HTTP_204_NO_CONTENT)