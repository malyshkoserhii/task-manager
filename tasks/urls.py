from django.urls import path
from django.contrib.auth import views as auth_views

from tasks.views import (
    index,
    ProjectsListView,
    RegisterUserView,
    ProjectCreateView,
    ProjectDeleteView,
    ProjectUpdateView,
    TeamsListView,
    TeamCreateView,
    TeamUpdateView,
    TeamDeleteView,
    TeamLeaveView,
)

urlpatterns = [
    # Public routes
    path("", index, name="index"),
    path("registration/", RegisterUserView.as_view(), name="registration"),
    # Private routes
    path("projects/", ProjectsListView.as_view(), name="project-list"),
    path("projects/create/", ProjectCreateView.as_view(), name="project-create"),
    path(
        "projects/<int:pk>/update/", ProjectUpdateView.as_view(), name="project-update"
    ),
    path(
        "projects/<int:pk>/delete/", ProjectDeleteView.as_view(), name="project-delete"
    ),
    path(
        "teams/", TeamsListView.as_view(), name="team-list"
    ),
    path("teams/create/", TeamCreateView.as_view(), name="team-create"),
    path(
        "teams/<int:pk>/update/", TeamUpdateView.as_view(), name="team-update"
    ),
    path(
        "teams/<int:pk>/delete/",
        TeamDeleteView.as_view(),
        name="team-delete",
    ),
    path(
        "teams/<int:pk>/leave/",
        TeamLeaveView.as_view(),
        name="team-leave",
    ),
    path(
        "password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change_form.html",
            success_url="/password-change/done/",
        ),
        name="password_change",
    ),
    path(
        "password-change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),
]

app_name = "tasks"
