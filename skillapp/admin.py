from django.contrib import admin
from .models import Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "category",
        "completed_hours",
        "target_hours",
        "last_practiced",
        "created_at",
    )

    list_filter = ("category", "user")
    search_fields = ("name", "user__username")