from django.shortcuts import render

# Create your views here.
def index(request, *args, **kwargs):
    return render(request,'frontend/index.html')

# allow us to render the index template and then the react takes care of this thing
