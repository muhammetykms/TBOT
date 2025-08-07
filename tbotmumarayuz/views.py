


from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
from tbotmumarayuz.decorators import check_user_authenticated

from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os

from django.http import HttpResponseRedirect
from django.urls import reverse







@check_user_authenticated
def home(request):
    show_block = True
    
    return render(request, 'home.html', {'show_block': show_block})
