from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path("add-hours/<int:skill_id>/", views.add_hours, name="add_hours"),
    path('delete-skill/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path('practice-recommended-skill/', views.practice_recommended_skill, name='practice_recommended_skill'),
]