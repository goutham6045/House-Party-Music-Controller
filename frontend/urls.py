from django.urls import path
from .views import index

app_name = 'frontend' # we are including this because django needs to know that there is the app called frontend as the redirect thing redirects to the frontend

urlpatterns = [
    path('', index, name=''),
    path('info', index),
    path('join', index),
    path('create', index),
    path('room/<str:roomCode>', index)
]
# when a blank url is typed in the webpage then the main url directs it into the frontend urls and that later will send to the views index file