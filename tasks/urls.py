from django.urls import path
from django.contrib.auth import views as auth_views

from tasks.views import index, ProjectsListView
from views import RegisterUserView

urlpatterns = [
    # Public routes
    path("", index, name="index"),
    path("registration/", RegisterUserView.as_view(), name="registration"),
    # Private routes
    path("projects/", ProjectsListView.as_view(), name="project-list"),
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
