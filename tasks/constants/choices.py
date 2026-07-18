from django.db import models


class Priority(models.IntegerChoices):
    URGENT = 1, "Urgent"
    HIGH = 2, "High"
    MEDIUM = 3, "Medium"
    LOW = 4, "Low"


class TaskStatus(models.TextChoices):
    TO_DO = "TO_DO", "To Do"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    TECH_REVIEW = "TECH_REVIEW", "Tech Review"
    QA = "QA", "QA"
    REWORK = "REWORK", "Rework"
    MERGED = "MERGED", "Merged"
    DEPLOYMENT = "DEPLOYMENT", "Deployment"
    DONE = "DONE", "Done"
    BACKLOG = "BACKLOG", "Backlog"
