from django.contrib.auth.models import AbstractUser
from django.db import models

from task_manager import settings
from tasks.constants.choices import Priority, TaskStatus


class TaskType(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "task type"
        verbose_name_plural = "task types"
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

    class Meta:
        verbose_name = "worker"
        verbose_name_plural = "workers"

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.username} ({self.first_name} {self.last_name})"
        return self.username


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
    teams = models.ManyToManyField(
        Team,
        related_name="projects",
        blank=True,
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_projects",
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    priority = models.IntegerField(
        choices=Priority,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=30, choices=TaskStatus, default=TaskStatus.TO_DO
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
    task_type = models.ForeignKey(
        TaskType, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks"
    )

    class Meta:
        ordering = ("priority", "-created_at")

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("task",)

    def __str__(self):
        return f"Author ID: {self.author.id}"
