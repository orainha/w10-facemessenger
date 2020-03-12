from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def home_view(request, *args, **kwargs):
    #return HttpResponse("<h1>Hello W</h1>")
    my_context = {
        "my_text" : "This is about us",
        "my_number": 123,
        "my_list": [123, 456, 904]
    }
    return render(request, "home.html", my_context)