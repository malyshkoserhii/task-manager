from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic

from forms.auth import WorkerCreationForm
from tasks.models import Project


def index(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("tasks:project-list")
    return render(request, "tasks/index.html")


class RegisterUserView(generic.CreateView):
    form_class = WorkerCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("tasks:index")


class ProjectsListView(LoginRequiredMixin, generic.ListView):
    model = Project
    paginate_by = 10
