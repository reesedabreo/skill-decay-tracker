import csv, os
import json
from django.conf import settings
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Skill
from django.db import models
from django.contrib import messages
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
    popup_recommendation = None

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        category = request.POST.get("category", "").strip()
        target_hours = request.POST.get("target_hours")

        if name and category and target_hours:
            existing_skill = Skill.objects.filter(
                user=request.user,
                name__iexact=name
            ).first()

            if not existing_skill:
                Skill.objects.create(
                    user=request.user,
                    name=name,
                    category=category,
                    target_hours=target_hours,
                    completed_hours=0
                )
                messages.success(request, f"{name} added successfully!")  

                skills_after_add = Skill.objects.filter(user=request.user)

                # only generate popup recommendations for the newly added skill
                popup_recommendations = recommend_skills([name.lower()], skills_after_add)

                # keep only recommendations based on the skill just added
                popup_recommendations = [
                    rec for rec in popup_recommendations
                    if rec["based_on"].strip().lower() == name.lower()
                ]

                if popup_recommendations:
                    popup_recommendation = popup_recommendations[0]
            else:
                messages.warning(request, f"{name} already exists.")
    skills = Skill.objects.filter(user=request.user)

    alerts = []
    for skill in skills:
        if skill.days_since_practice > 7:
            alerts.append({
                "type": "warning",
                "message": f"You haven’t practiced {skill.name} for {skill.days_since_practice} days"
            })

        if skill.risk_level == "High":
            alerts.append({
                "type": "danger",
                "message": f"{skill.name} is at HIGH risk — practice immediately!"
            })
        elif skill.risk_level == "Medium":
            alerts.append({
                "type": "info",
                "message": f"{skill.name} needs attention"
            })

    unique_skills = {}
    for skill in skills:
        unique_skills[skill.name] = skill.health_score

    skill_names = json.dumps(list(unique_skills.keys()))
    health_scores = json.dumps(list(unique_skills.values()))

    user_skills = [skill.name.lower() for skill in skills]
    recommendations = recommend_skills(user_skills, skills)

    top_action = None
    if recommendations:
        top = recommendations[0]
        top_action = f"Focus on {top['skill']} — high demand & your {top['based_on']} skill is weakening"

    total_skills = skills.count()

    healthy_skills = sum(1 for skill in skills if skill.risk_level == "Low")
    at_risk_skills = sum(1 for skill in skills if skill.risk_level in ["Medium", "High"])

    avg_health = round(
        sum(skill.health_score for skill in skills) / total_skills, 1
    ) if total_skills > 0 else 0

    strongest_skill = max(skills, key=lambda s: s.health_score, default=None)
    weakest_skill = min(skills, key=lambda s: s.health_score, default=None)
    most_neglected_skill = max(skills, key=lambda s: s.days_since_practice, default=None)

    return render(request, "dashboard.html", {
        "skills": skills,
        "total_skills": total_skills,
        "healthy_skills": healthy_skills,
        "at_risk_skills": at_risk_skills,
        "avg_health": avg_health,
        "strongest_skill": strongest_skill,
        "weakest_skill": weakest_skill,
        "most_neglected_skill": most_neglected_skill,
        "recommendations": recommendations,
        "top_action": top_action,
        "skill_names": skill_names,
        "health_scores": health_scores,
        "alerts": alerts,
        "popup_recommendation": popup_recommendation,
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
            messages.success(request, f"{hours} hours added to {skill.name}.")

    return redirect("dashboard")

@login_required
def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, user=request.user)

    if request.method == "POST":
        skill_name = skill.name
        skill.delete()
        messages.success(request, f"{skill_name} deleted successfully.")

    return redirect("dashboard")


@login_required
def practice_recommended_skill(request):
    if request.method == "POST":
        skill_name = request.POST.get("skill_name", "").strip()
        category = request.POST.get("category", "Recommended").strip()

        if skill_name:
            existing_skill = Skill.objects.filter(
                user=request.user,
                name__iexact=skill_name
            ).first()

            if not existing_skill:
                Skill.objects.create(
                    user=request.user,
                    name=skill_name,
                    category=category,
                    target_hours=30,
                    completed_hours=0
                )   
                messages.success(request, f"{skill_name} added to your skills.")    

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

def recommend_skills(user_skills, skills):
    dataset = load_dataset()
    recommendations = []

    for row in dataset:
        skill_text = row['skill'].strip().lower()
        alternatives = row['modern_alternatives']
        demand = int(row['demand_score'])
        category = row['category']

        matched_user_skill = None
        user_health = 50

        for skill in skills:
            db_skill = skill.name.strip().lower()

            # Better two-way matching
            if (
                skill_text == db_skill
                or skill_text in db_skill
                or db_skill in skill_text
            ):
                matched_user_skill = skill.name
                user_health = skill.health_score
                break

        if matched_user_skill and demand >= 60:
            for alt in alternatives.split(','):
                alt = alt.strip()

                # do not recommend a skill user already has
                if alt.lower() in [s.name.lower() for s in skills]:
                    continue

                priority = int((100 - user_health) * 0.6 + demand * 0.4)

                recommendations.append({
                    "skill": alt,
                    "based_on": matched_user_skill,
                    "demand": demand,
                    "category": category,
                    "priority": priority,
                    "reason": f"{matched_user_skill} is weakening, {alt} is trending in market"
                })

    if not recommendations:
        recommendations = [{
            "skill": "Communication Skills",
            "based_on": "General",
            "demand": 90,
            "category": "Soft Skills",
            "priority": 80,
            "reason": "Useful across all domains"
        }]

    # Deduplicate by recommended skill, keep highest priority
    unique_recommendations = {}
    for rec in recommendations:
        key = rec["skill"].lower()
        if key not in unique_recommendations or rec["priority"] > unique_recommendations[key]["priority"]:
            unique_recommendations[key] = rec

    recommendations = list(unique_recommendations.values())

    recommendations = sorted(
        recommendations,
        key=lambda x: x.get("priority", 0),
        reverse=True
    )

    return recommendations