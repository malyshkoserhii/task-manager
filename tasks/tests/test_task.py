from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from constants.choices import TaskStatus, Priority
from forms.task import TaskCreateForm
from tasks.models import Project, TaskType, Task


class TaskTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="Test123!",
        )

        self.client.force_login(self.user)

        self.project = Project.objects.create(
            name="Test Project",
            description="Test description",
            creator=self.user,
        )

        self.backend = TaskType.objects.create(
            name="Backend",
        )
        self.frontend = TaskType.objects.create(
            name="Frontend",
        )

        self.now = timezone.now()

        self.task1 = Task.objects.create(
            name="Create auth flow",
            description="Create auth flow for mobile App",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.HIGH,
            task_type=self.backend,
            project=self.project,
            deadline=self.now + timedelta(days=1),
        )
        self.task1.assignees.add(self.user.id)
        Task.objects.filter(pk=self.task1.pk).update(
            created_at=self.now - timedelta(days=2)
        )
        self.task1.refresh_from_db()

        self.task2 = Task.objects.create(
            name="Setup React Native Project",
            description="Setup repository and RN environment",
            status=TaskStatus.TO_DO,
            priority=Priority.URGENT,
            task_type=self.backend,
            project=self.project,
            deadline=self.now + timedelta(days=1),
        )
        self.task2.assignees.add(self.user.id)
        Task.objects.filter(pk=self.task2.pk).update(
            created_at=self.now - timedelta(days=1)
        )
        self.task2.refresh_from_db()

        another_user = get_user_model().objects.create_user(
            username="another_user",
            password="Test123!",
        )
        self.task3 = Task.objects.create(
            name="Write tests for auth flow",
            description="Only testing",
            status=TaskStatus.TO_DO,
            priority=Priority.URGENT,
            task_type=self.backend,
            project=self.project,
            deadline=self.now + timedelta(days=1),
        )
        self.task3.assignees.add(another_user.id)
        Task.objects.filter(pk=self.task3.pk).update(
            created_at=self.now - timedelta(days=1)
        )
        self.task3.refresh_from_db()

    def test_past_deadline_error(self):
        past_time = timezone.now() - timedelta(hours=1)
        form_data = {
            "name": "Invalid Task",
            "description": "Some description",
            "status": TaskStatus.IN_PROGRESS,
            "priority": Priority.HIGH,
            "task_type": self.backend.id,
            "project": self.project.id,
            "deadline": past_time,
            "assignees": [str(self.user.id)],
        }
        form = TaskCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("deadline", form.errors)
        self.assertEqual(
            form.errors["deadline"][0], "Deadline cannot be less than current time."
        )

    def test_future_deadline_success(self):
        future_time = timezone.now() + timedelta(days=3)
        form_data = {
            "name": "Valid Task",
            "description": "Some description",
            "status": TaskStatus.TO_DO,
            "priority": Priority.URGENT,
            "task_type": self.backend.id,
            "project": self.project.id,
            "deadline": future_time,
            "assignees": [str(self.user.id)],
        }

        form = TaskCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.is_valid())

    def test_task_list_filtration_by_name(self):
        url = reverse("tasks:project-tasks", kwargs={"pk": self.project.pk})
        response = self.client.get(url, {"name": "auth"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.task1, response.context["tasks"])
        self.assertIn(self.task3, response.context["tasks"])
        self.assertNotIn(self.task2, response.context["tasks"])

    def test_task_list_filtration_by_assignee(self):
        url = reverse("tasks:project-tasks", kwargs={"pk": self.project.pk})

        # Here should be assignee but not assignees,
        # because in TaskSearchForm defined assignee field
        response = self.client.get(url, {"assignee": self.user.id})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.task1, response.context["tasks"])
        self.assertIn(self.task2, response.context["tasks"])
        self.assertNotIn(self.task3, response.context["tasks"])

    def test_task_list_filtration_by_assignee_and_name(self):
        url = reverse("tasks:project-tasks", kwargs={"pk": self.project.pk})

        # Here should be assignee but not assignees,
        # because in TaskSearchForm defined assignee field
        response = self.client.get(url, {"assignee": self.user.id, "name": "auth"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.task1, response.context["tasks"])
        self.assertNotIn(self.task2, response.context["tasks"])
        self.assertNotIn(self.task3, response.context["tasks"])

    def test_task_list_sorting_by_deadline_asc(self):
        url = reverse("tasks:project-tasks", kwargs={"pk": self.project.pk})

        task_far_deadline = Task.objects.create(
            name="Far deadline task",
            description="Testing sorting",
            status=TaskStatus.TO_DO,
            priority=Priority.URGENT,
            task_type=self.backend,
            project=self.project,
            deadline=self.now + timedelta(days=10),
        )

        response = self.client.get(url, {"deadline": "deadline_asc"})
        self.assertEqual(response.status_code, 200)

        tasks_in_context = list(response.context["tasks"])

        self.assertLess(
            tasks_in_context.index(self.task1),
            tasks_in_context.index(task_far_deadline),
        )
        self.assertLess(
            tasks_in_context.index(self.task2),
            tasks_in_context.index(task_far_deadline),
        )

    def test_task_list_sorting_by_created_at_desc(self):
        url = reverse("tasks:project-tasks", kwargs={"pk": self.project.pk})
        response = self.client.get(url, {"sort": "-created_at"})
        self.assertEqual(response.status_code, 200)
        tasks_in_context = list(response.context["tasks"])
        self.assertEqual(tasks_in_context[2], self.task1)
        self.assertLess(
            tasks_in_context.index(self.task2), tasks_in_context.index(self.task1)
        )
        self.assertLess(
            tasks_in_context.index(self.task3), tasks_in_context.index(self.task1)
        )
