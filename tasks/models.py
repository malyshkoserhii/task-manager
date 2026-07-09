from django.contrib.auth.models import AbstractUser
from django.db import models

from task_manager import settings
from tasks.constants.choices import PRIORITY_CHOICES


class TaskType(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "task_type"
        verbose_name_plural = "task_types"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workers",
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="teams",
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    team = models.ManyToManyField(Team, related_name="projects")

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    deadline = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES.items(),
        default=PRIORITY_CHOICES.get("MEDIUM"),
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="tasks",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    class Meta:
        ordering = ("deadline",)

    def __str__(self):
        deadline = self.deadline.strftime("%d-%m-%Y")
        return f"{self.name}, {deadline}"


class Comment(models.Model):
    text = models.TextField()
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    class Meta:
        ordering = ("task",)

    def __str__(self):
        return f"Author ID: {self.author.id}"


class Like(models.Model):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["comment", "user"],
                name="unique_like_comment_user",
            )
        ]
