from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Skill
from django.db import models
from django.contrib.auth.models import User
from datetime import date
def index_view(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "Username already exists"
            })

        if User.objects.filter(email=email).exists():
            return render(request, "register.html", {
                "error": "Email already registered"
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect("dashboard")

    return render(request, "register.html")
@login_required
def dashboard_view(request):

    if request.method == "POST":
        name = request.POST.get("name")
        category = request.POST.get("category")
        target_hours = request.POST.get("target_hours")

        if name and category and target_hours:
            Skill.objects.create(
                user=request.user,
                name=name,
                category=category,
                target_hours=target_hours,
                completed_hours=0
            )
            return redirect("dashboard")  # prevents duplicate submission

    skills = Skill.objects.filter(user=request.user)
     
    # ---- COUNTERS ----
    total_skills = skills.count()

    healthy_skills = skills.filter(
        completed_hours__gte=models.F('target_hours')
    ).count()

    at_risk_skills = skills.filter(
        completed_hours__lt=models.F('target_hours')
    ).count()

    return render(request, "dashboard.html", {
        "skills": skills,
        "total_skills": total_skills,
        "healthy_skills": healthy_skills,
        "at_risk_skills": at_risk_skills,
    })
@login_required
def add_hours(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)

    if request.method == "POST":
        hours = int(request.POST.get("hours", 0))
        if hours > 0:
            skill.completed_hours += hours
            skill.last_practiced = date.today()
            skill.save()

    return redirect("dashboard")

def logout_view(request):
    logout(request)
    return redirect('index')