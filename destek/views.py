from django.shortcuts import render

# Create your views here.

def destek_index(request):
    

    return render(request, "destek/destek_index.html")
