from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic

from tasks.forms.team import TeamCreateForm
from tasks.forms.auth import WorkerCreationForm
from tasks.forms.project import ProjectCreateForm, ProjectSearchForm
from tasks.models import Project, Team


User = get_user_model()


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
    paginate_by = 6
    context_object_name = "projects"

    def get_queryset(self):
        queryset = Project.objects.filter(
            Q(creator=self.request.user) | Q(teams__members=self.request.user)
        ).distinct()
        form = ProjectSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["project_search_form"] = ProjectSearchForm(initial={"name": name})
        return context


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    form_class = ProjectCreateForm
    success_url = reverse_lazy("tasks:project-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Project
    form_class = ProjectCreateForm
    success_url = reverse_lazy("tasks:project-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Project
    template_name = "tasks/project_confirm_delete.html"
    success_url = reverse_lazy("tasks:project-list")


class TeamsListView(LoginRequiredMixin, generic.ListView):
    model = Team
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_users_count"] = User.objects.count
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(members=self.request.user)


class TeamCreateView(LoginRequiredMixin, generic.CreateView):
    model = Team
    form_class = TeamCreateForm
    success_url = reverse_lazy("tasks:team-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.object:
            self.object.members.add(self.request.user)

        return response


class TeamUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Team
    form_class = TeamCreateForm
    success_url = reverse_lazy("tasks:team-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class TeamDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Team
    success_url = reverse_lazy("tasks:team-list")


class TeamLeaveWarningView(LoginRequiredMixin, generic.DeleteView):
    model = Team
    template_name = "tasks/team_delete_confirm.html"


class TeamLeaveView(LoginRequiredMixin, generic.DetailView):
    model = Team
    template_name = "tasks/team_leave_confirm.html"

    def post(self, request, *args, **kwargs):
        team = self.get_object()
        team.members.remove(request.user)
        return redirect("tasks:team-list")
