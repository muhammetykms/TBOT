from django.shortcuts import render

# Create your views here.

def islemac_index(request):
    
    context={}
    return render(request, "islemac_index.html", context)
