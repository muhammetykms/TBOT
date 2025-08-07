
import requests
from django.shortcuts import render
from django.http import JsonResponse
import subprocess
# Create your views here.
def servisler_index(request):
    try:
        response = requests.get('http://127.0.0.1:8000/')  # FastAPI mikro servisine istek gönder
        data = response.json()  # JSON yanıtını al
    except requests.exceptions.RequestException as e:
        context = {'error': f'FastAPI servisine bağlanılamadı: {e}'}


    return render(request, "servisler/servisler_index.html", context)


def check_fastapi_service(request):
    try:
        response = requests.post('http://127.0.0.1:8001/start/m7cg5aq')  # FastAPI mikro servisine istek gönder
        data = response.json()  # JSON yanıtını al
    except requests.exceptions.RequestException as e:
        data = {'error': f'FastAPI servisine bağlanılamadı: {e}'}

    return render(request, 'check_service.html', {'data': data})
