from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import LoginActivity, SearchLog
import json


def index(request):
    return render(request, "index.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("/home/")
        return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")



@login_required(login_url="/login/")
def dashboard(request):
    logins = LoginActivity.objects.order_by('-login_time')[:10]
    searches = SearchLog.objects.order_by('-timestamp')[:10]

    return render(request, "dashboard.html", {
        "logins": logins,
        "searches": searches
    })



@staff_member_required
def activity_dashboard(request):
    logins = LoginActivity.objects.order_by("-login_time")
    searches = SearchLog.objects.order_by("-timestamp")

    return render(request, "activity_dashboard.html", {
        "logins": logins,
        "searches": searches
    })


# ---------------- SEARCH LOGGING ----------------
@csrf_exempt
def log_search(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        location = data.get('location', '')
        skill = data.get('skill', '')
        year = data.get('year', '')
        user = request.user if request.user.is_authenticated else None

        SearchLog.objects.create(
            user=user,
            location=location,
            skill=skill,
            year=year
        )
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)


# ---------------- ANALYSIS PAGE ----------------
@login_required(login_url="/login/")
def analysis_view(request):
    skill = request.GET.get('skill')
    year = request.GET.get('year')
    location = request.GET.get('location')

    if skill and year and location:
        SearchLog.objects.create(
            user=request.user,
            location=location,
            skill=skill,
            year=year
        )

    return render(request, 'analysis.html', {
        'skill': skill or '',
        'year': year or '',
        'location': location or '',
    })


def signup_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("username") 
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(request, "signup.html", {"error": "Passwords do not match!"})

        if User.objects.filter(username=email).exists():
            return render(request, "signup.html", {"error": "Email already registered!"})
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1
        )

        user.first_name = full_name
        user.save()

        messages.success(request, "Account created successfully!")
        return redirect("login")

    return render(request, "signup.html")

def introduction(request):
    return redirect("home")


def about_page(request):
    return render(request, 'about.html')

def insights(request):
    return render(request,'insights.html')

def trend_view(request):

    context = {
        "year": "2026",
        "top_skill": "AI / Machine Learning",
        "top_city": "Delhi",
        "market_trend": "Strong Upward Momentum",

        "growing_skills": [
            {
                "name": "AI / ML",
                "growth": 45,
                "description": "High adoption across fintech, healthcare, and automation sectors."
            },
            {
                "name": "Cybersecurity",
                "growth": 32,
                "description": "Rising due to data protection regulations and cyber threats."
            }
        ],

        "stable_skills": [
            {
                "name": "Java",
                "description": "Enterprise backbone technology with steady hiring demand."
            },
            {
                "name": "SQL",
                "description": "Consistent demand in backend and analytics roles."
            }
        ],

        "declining_skills": [
            {
                "name": "Legacy PHP",
                "description": "Reduced demand as modern frameworks dominate."
            }
        ]
    }

    return render(request, "trend.html", context)


def course(request):
    return render(request, "course.html")


def jobs_page(request):
    return render(request, "jobs.html")    


def job_detail(request, job_id):
    from django.shortcuts import get_object_or_404, render
    from .models import JobPosting

    job = get_object_or_404(JobPosting, id=job_id, is_active=True)

    return render(request, "job_detail.html", {"job": job})  