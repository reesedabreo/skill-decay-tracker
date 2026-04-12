from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Skill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    target_hours = models.IntegerField()
    completed_hours = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_practiced = models.DateField(default=date.today)

    @property
    def progress(self):
        if self.target_hours > 0:
            percentage = int((self.completed_hours / self.target_hours) * 100)
            return min(percentage, 100)
        return 0

    @property
    def days_since_practice(self):
        return (date.today() - self.last_practiced).days
    
    @property
    def health_score(self):
        score = 100
        score -= self.days_since_practice * 4   # lose 4 points per day
        score += self.progress * 0.3           # progress adds stability

        return max(0, min(100, int(score)))
    
    @property
    def risk_level(self):
        if self.health_score >= 70:
            return "Low"
        elif self.health_score >= 40:
            return "Medium"
        else:
            return "High" 
        
    def __str__(self):
        return self.name
    
    @property
    def future_risk(self):
    # simulate 7 days ahead
        future_days = self.days_since_practice + 7

        future_score = self.progress - (future_days * 3)

        if future_score < 30:
            return "High"
        elif future_score < 60:
            return "Medium"
        else:
            return "Low"    