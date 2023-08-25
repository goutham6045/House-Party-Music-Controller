from django.shortcuts import render
from rest_framework import generics, status
# ( gives us the status or the http statuscodes)
from .serializers import RoomSerializer, CreateRoomSerializer,UpdateRoomSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse

# Create your views here.
# endpoint of the webpage which is accessed when typed in a url 
# and now we've to figure out the endpoints and add all the endpoint urls in the urls.py
#API view

class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class GetRoom(APIView):
    serializer_class = RoomSerializer
    lookup_url_kwarg='code'
    # when we call ther getRoom in the api when the get request is made, it will take the code and the code is retrieved.
    def get(self,request,format=None):
        code=request.GET.get(self.lookup_url_kwarg)
        if code !=None:
            room = Room.objects.filter(code=code)
            if len(room)>0:
                data=RoomSerializer(room[0]).data
                data['is_host']=self.request.session.session_key==room[0].host
                return Response(data, status=status.HTTP_200_OK)# if the key is present we return the message as the room is created and the status is Ok
            # but when the room is not created using the code , we send a response with status code 404 
            return Response({'Bad Request': 'Invalid Room Code'}, status=status.HTTP_404_NOT_FOUND)
        #if the code is not present , we didnt get the correct data to land into the Room created page.
        return Response({'Bad Request': 'Code Parameter is not Found in the Request'}, status=status.HTTP_404_NOT_FOUND)

# user will send the code and then we chack if it is valid code, if it is then we create a new session.

class JoinRoom(APIView):
    lookup_url_kwarg='code'
    def post(self,request,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        code=request.data.get(self.lookup_url_kwarg)
        if code!=None:
            room_result =Room.objects.filter(code=code)
            if len(room_result)>0:
                room = room_result[0]
                self.request.session['room_code'] = code 
                # note in the backend that the this user is in the present room 
                return Response({'Message': 'Room Successfully Joined'}, status=status.HTTP_200_OK)
            return Response({'Bad Request': 'Invalid Room Code'}, status= status.HTTP_400_BAD_REQUEST) 
        return Response({'Bad Request': 'Invalid post Data'}, status= status.HTTP_400_BAD_REQUEST)    

class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer
    #api view overrides some basic default methods such as get, post, retrieve
    #seesion is stored in memory and each user will have unique session
    def post(self, request, format = None):
        #if there is no existing session created by the user then we create 
        #a new session for the user and it take the userid
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        
        serializer = self.serializer_class(data=request.data)  
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause',False)
            votes_to_skip = serializer.data.get('votes_to_skip',1)
            host = self.request.session.session_key
            queryset = Room.objects.filter(host=host)
            if queryset.exists():
                room = queryset[0]
                room.guest_can_pause = guest_can_pause 
                room.votes_to_skip = votes_to_skip 
                room.save(update_fields=['guest_can_pause','votes_to_skip'])
                self.request.session['room_code']=room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
            else:
                room = Room(host=host,guest_can_pause=guest_can_pause,votes_to_skip=votes_to_skip)
                room.save()
                self.request.session['room_code']=room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
        return Response({'Bad Request': 'Invalid Data'}, status= status.HTTP_400_BAD_REQUEST)

# this view is used to send a get request for the desired endpoint and the endpoint will check if the user is in the room session, if they are it will return that room code?
class UserInRoom(APIView):
    
    def get (self , request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        
        data={
            'code' : self.request.session.get('room_code')
        }
        return JsonResponse(data, status=status.HTTP_200_OK)
# we are making a post request because we are changing the information on the server, as we are removing the matter from the webpage
class LeaveRoom(APIView):
    def post(self,request,format=None):
        if 'room_code' in self.request.session:
            self.request.session.pop("room_code")
            #here we store the code because we need to check that if the code given is by the host, if it the host then we need to delete the room.
            host_id=self.request.session.session_key
            # we need to do a query on all the objects and see if this user is the host.
            # If yes delete that object from database and the room should be closed.
            room_results= Room.objects.filter(host=host_id)
            if room_results.exists():
                room = room_results[0]
                room.delete()
        
        return Response({'Message': 'Success'}, status=status.HTTP_200_OK)
    

class UpdateRoom(APIView):
    serializer_class = UpdateRoomSerializer
    def patch(self,request,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause',False)
            votes_to_skip = serializer.data.get('votes_to_skip',1)
            code=serializer.data.get('code')
            queryset=Room.objects.filter(code=code)
            if not queryset.exists():
                return Response({"Error": "No Such Code"}, status=status.HTTP_404_NOT_FOUND)
            room=queryset[0]
            user_id=self.request.session.session_key
            if room.host!=user_id:
                return Response({'Message': 'You are not the host of this room.'},status=status.HTTP_403_FORBIDDEN)
            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
            return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
        return Response({'Bad Request': "Invalid Data..."}, status=status.HTTP_400_BAD_REQUEST)