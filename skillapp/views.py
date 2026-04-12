import csv, os
from django.conf import settings
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
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
    skill_names = [skill.name for skill in skills]
    health_scores = [skill.health_score for skill in skills]
    user_skills = [skill.name.lower() for skill in skills]
    recommendations = recommend_skills(user_skills)
    top_action = None

    if recommendations:
       top = recommendations[0]
       top_action = f"Focus on {top['skill']} (based on {top['based_on']})" 
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
        "recommendations": recommendations,
        "top_action": top_action,
         "skill_names": skill_names,
         "health_scores": health_scores,
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

def load_dataset():
    dataset = []
    path = os.path.join(settings.BASE_DIR, 'dataset', 'skills_dataset.csv')

    with open(path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            dataset.append(row)

    return dataset

def recommend_skills(user_skills):
    dataset = load_dataset()
    recommendations = []

    user_text = " ".join(user_skills)

    for row in dataset:
        skill_text = row['skill']
        alternatives = row['modern_alternatives']
        demand = int(row['demand_score'])
        category = row['category']

        texts = [user_text, skill_text]
        vectorizer = CountVectorizer().fit_transform(texts)
        similarity = cosine_similarity(vectorizer)[0][1]

        if similarity > 0.3 or any(uskill in skill_text.lower() for uskill in user_skills):
            if demand >= 85:
                for alt in alternatives.split(','):
                    recommendations.append({
                        "skill": alt.strip(),
                        "based_on": skill_text,
                        "demand": demand,
                        "category": category
                    })

    if not recommendations:
        recommendations = [{
            "skill": "Communication Skills",
            "based_on": "General",
            "demand": 90,
            "category": "Soft Skills"
        }]

    return recommendations