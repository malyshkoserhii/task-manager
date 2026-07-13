from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from tasks.forms.project import ProjectCreateForm, ProjectSearchForm
from tasks.models import Team, Project

User = get_user_model()


class ProjectBusinessLogicTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="serhii",
            password="Test123!",
        )
        self.other_user = User.objects.create_user(
            username="natali",
            password="Test123!",
        )

        self.my_team = Team.objects.create(
            name="Mobile Dev Team",
        )
        self.my_team.members.add(self.user)
        self.other_team = Team.objects.create(
            name="Backend Dev Team",
        )
        self.other_team.members.add(self.other_user)

        self.p1 = Project.objects.create(
            name="AI Money Tracker",
            creator=self.user,
        )
        self.p2 = Project.objects.create(
            name="SaaS Platform",
            creator=self.other_user,
        )
        self.p2.teams.add(self.my_team)
        self.p3 = Project.objects.create(
            name="Secret Crypto",
            creator=self.other_user,
        )
        self.p3.teams.add(self.other_team)

    def test_custom_queryset_limit(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tasks:project-list"))
        projects = response.context["projects"]
        self.assertEqual(len(projects), 2)
        self.assertIn(self.p1, projects)
        self.assertIn(self.p2, projects)
        self.assertNotIn(self.p3, projects)

    def test_custom_queryset_filter(self):
        form = ProjectCreateForm(
            user=self.user,
        )
        teams_in_form = form.fields["teams"].queryset
        self.assertIn(self.my_team, teams_in_form)
        self.assertNotIn(self.other_team, teams_in_form)

    def test_search_my_projects_not_empty(self):
        form_data = {
            "name": "money"
        }
        form = ProjectSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, form_data)

    def test_search_my_projects_empty(self):
        form_data = {
            "name": ""
        }
        form = ProjectSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, form_data)

    def test_search_project_form_label_and_placeholder(self):
        form = ProjectSearchForm()
        self.assertEqual(form.fields["name"].label, "")
        self.assertEqual(
            form.fields["name"].widget.attrs["placeholder"],
            "Search project by name"
        )
