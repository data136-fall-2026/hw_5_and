"""
views.py — HTTP request handlers for AttendanceChimp.

Each view corresponds to one URL endpoint.  Views receive an HTTP request,
interact with the database via models.py, and return an HTTP response.
"""

from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime
import zoneinfo
import json
import io

from .models import (InstructorProfile, StudentProfile, Course, Enrollment,
                     Lecture, QRCodeUpload, is_instructor, is_student)

CDT = zoneinfo.ZoneInfo("America/Chicago")


# ---------------------------------------------------------------------------
# HW2 — time, sum 
# ---------------------------------------------------------------------------

@csrf_exempt
def time_view(request):
    """Return the current Chicago time as HH:MM."""
    if request.method != "GET":
        return HttpResponse("Error: only GET is allowed", status=405)
    now = datetime.now().astimezone(CDT)
    return HttpResponse(now.strftime("%H:%M"))


@csrf_exempt
def sum_view(request):
    """Return the sum of query parameters n1 and n2."""
    if request.method != "GET":
        return HttpResponse("Error: only GET is allowed", status=405)
    try:
        n1 = float(request.GET['n1'])
        n2 = float(request.GET['n2'])
    except (KeyError, ValueError):
        return HttpResponse("Error: provide numeric n1 and n2", status=400)
    result = n1 + n2
    if result == int(result):
        return HttpResponse(str(int(result)))
    return HttpResponse(str(result))


# ---------------------------------------------------------------------------
# HW4  — index, user creation
# ---------------------------------------------------------------------------

def new(request):
    """Render the sign-up form (GET only)."""
    if request.method != "GET":
        return HttpResponse("Error: only GET is allowed", status=405)
    return render(request, 'app/new.html')

def index(request):
    """Render the home page (index.html)."""
    now = datetime.now().astimezone(CDT)
    context = {
        'current_time': now.strftime("%H:%M"),
        'user': request.user,
    }
    return render(request, 'app/index.html', context)

@csrf_exempt
def createUser(request):
    """Create a new student or instructor user (POST only)."""
    if request.method != "POST":
        return HttpResponse("Error: only POST is allowed", status=405)
    try:
        user_name = request.POST['user_name']
        password = request.POST['password']
        email = request.POST['email']
        is_student_flag = request.POST.get('is_student', '1')
    except KeyError:
        return HttpResponse("Error: missing required fields", status=400)

    if User.objects.filter(email=email).exists():
        return HttpResponse("Error: email already in use", status=400)
    if User.objects.filter(username=user_name).exists():
        return HttpResponse("Error: user name already in use", status=400)

    user = User.objects.create_user(username=user_name, password=password,
                                    email=email)
    if str(is_student_flag) in ('1', 'true', 'True', 'on'):
        StudentProfile.objects.create(user=user)
    else:
        InstructorProfile.objects.create(user=user)

    user = authenticate(username=user_name, password=password)
    if user is not None:
        login(request, user)
    return HttpResponse("User created successfully", status=200)

