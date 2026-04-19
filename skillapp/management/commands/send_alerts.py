from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from skillapp.models import Skill
from django.core.mail import send_mail
from datetime import date
import os
print("Running from:", os.getcwd())

class Command(BaseCommand):
    help = "Send daily skill alerts"

    def handle(self, *args, **kwargs):

        users = User.objects.all()

        for user in users:
            skills = Skill.objects.filter(user=user)

            alerts = []

            for skill in skills:
                days = (date.today() - skill.last_practiced).days

                if days > 7:
                    alerts.append(f"You haven’t practiced {skill.name} for {days} days")

                if skill.risk_level == "High":
                    alerts.append(f"{skill.name} is at HIGH risk — practice immediately!")

            if alerts and user.email:
                send_mail(
                    subject="SkillDK Daily Alert 🚨",
                    message="\n".join(alerts),
                    from_email="skilldk@example.com",
                    recipient_list=[user.email],
                    fail_silently=True,
                )

        self.stdout.write(self.style.SUCCESS("Emails sent successfully"))