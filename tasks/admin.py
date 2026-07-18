from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from tasks.models import Worker, Project, TaskType, Position, Team, Task, Comment


@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    pass


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    search_fields = ["username", "first_name", "last_name"]
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional info",
            {"classes": ("wide",), "fields": ("position",)},
        ),
    )
    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional info",
            {
                "fields": ("position",),
            },
        ),
    )
    list_display = UserAdmin.list_display + ("position",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    autocomplete_fields = ["members"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "short_description",
        "status",
        "priority",
        "deadline",
        "project",
    )
    list_filter = ("status", "priority")
    search_fields = ("name",)

    def short_description(self, obj):
        if not obj.description:
            return ""
        if len(obj.description) > 50:
            return f"{obj.description[:50]}..."
        return obj.description

    short_description.short_description = "Description"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
