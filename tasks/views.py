from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Q, Count
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

from forms.task import TaskCreateForm, TaskSearchForm
from tasks.forms.team import TeamCreateForm
from tasks.forms.auth import WorkerCreationForm
from tasks.forms.project import ProjectCreateForm, ProjectSearchForm
from tasks.models import Project, Team, Task

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
    template_name = "tasks/team_confirm_delete.html"


class TeamLeaveView(LoginRequiredMixin, generic.DetailView):
    model = Team
    template_name = "tasks/team_leave_confirm.html"

    def post(self, request, *args, **kwargs):
        team = self.get_object()
        team.members.remove(request.user)
        return redirect("tasks:team-list")


class ProjectTaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    template_name = "tasks/project_task_list.html"  # Твій шлях до темплейту
    context_object_name = "tasks"
    paginate_by = 10
    project = None

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = (
            Task.objects.filter(project=self.project)
            .select_related("task_type")
            .prefetch_related("assignees")
        )

        form = TaskSearchForm(self.request.GET)
        if not form.is_valid():
            return queryset

        queryset = self._apply_filters(queryset, form.cleaned_data)
        queryset = self._apply_sorting(queryset, form.cleaned_data)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project

        if self.request.GET:
            context["task_search_form"] = TaskSearchForm(self.request.GET)
        else:
            context["task_search_form"] = TaskSearchForm()

        context["stats"] = Task.objects.filter(project=self.project).aggregate(
            total=Count("id"),
            done=Count("id", filter=Q(status="DONE")),
            in_progress=Count("id", filter=Q(status="IN_PROGRESS")),
            overdue=Count(
                "id", filter=Q(deadline__lt=timezone.now()) & ~Q(status="DONE")
            ),
        )

        return context

    def _apply_filters(self, queryset, cleaned_data):
        """Внутрішній метод для послідовної фільтрації тасок."""
        name = cleaned_data.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        status = cleaned_data.get("status")
        if status:
            queryset = queryset.filter(status=status)

        priority = cleaned_data.get("priority")
        if priority:
            queryset = queryset.filter(priority=priority)

        assignees = cleaned_data.get("assignee")
        if assignees:
            queryset = queryset.filter(assignees=assignees)

        task_type = cleaned_data.get("task_type")
        if task_type:
            queryset = queryset.filter(task_type=task_type)

        return queryset

    def _apply_sorting(self, queryset, cleaned_data):
        """Внутрішній метод для збору правил сортування та їх застосування."""
        sorting_rules = []

        deadline = cleaned_data.get("deadline")
        if deadline == "deadline_asc":
            sorting_rules.append(models.F("deadline").asc(nulls_last=True))
        elif deadline == "deadline_desc":
            sorting_rules.append(models.F("deadline").desc(nulls_last=True))

        created_at = cleaned_data.get("created_at")
        if created_at == "created_at_asc":
            sorting_rules.append(models.F("created_at").asc())
        elif created_at == "created_at_desc":
            sorting_rules.append(models.F("created_at").desc())

        if sorting_rules:
            queryset = queryset.order_by(*sorting_rules)

        return queryset


class ProjectTaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskCreateForm
    project = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        project_id = self.kwargs.get("pk")
        self.project = get_object_or_404(Project, pk=project_id)

    def form_valid(self, form):
        task = form.save(commit=False)
        task.project = self.project
        task.save()
        form.save_m2m()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:project-tasks", kwargs={"pk": self.project.id})

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        return context


class ProjectTaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskCreateForm
    project = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, **kwargs)
        project_id = self.kwargs.get("project_pk")
        self.project = get_object_or_404(Project, pk=project_id)

    def get_queryset(self):
        return Task.objects.filter(project=self.project)

    def form_valid(self, form):
        task = form.save(commit=False)
        task.project = self.project
        task.save()
        form.save_m2m()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("tasks:project-tasks", kwargs={"pk": self.project.id})

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        context["is_update"] = True
        return context


class ProjectTaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    project = None
    template_name = "tasks/task_detail.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, **kwargs)
        project_id = self.kwargs.get("project_pk")
        self.project = get_object_or_404(Project, pk=project_id)

    def get_queryset(self):
        return Task.objects.filter(project=self.project)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        return context


class ProjectTaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    project = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, **kwargs)
        project_id = self.kwargs.get("project_pk")
        self.project = get_object_or_404(Project, pk=project_id)

    def get_queryset(self):
        return Task.objects.filter(project=self.project)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        return context

    def get_success_url(self):
        return reverse_lazy("tasks:project-tasks", kwargs={"pk": self.project.id})
