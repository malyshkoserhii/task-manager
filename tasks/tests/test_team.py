from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from tasks.models import Team

User = get_user_model()


class TeamTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.frodo = User.objects.create_user(
            username="frodo",
            password="Test123!",
        )
        self.bilbo = User.objects.create_user(
            username="bilbo",
            password="Test123!",
        )
        self.gandalf = User.objects.create_user(
            username="gandalf",
            password="Test123!",
        )
        self.aragorn = User.objects.create_user(
            username="aragorn",
            password="Test123!",
        )

        self.frodo_team = Team.objects.create(
            name="Frodo Team",
        )
        self.frodo_team.members.add(self.frodo)
        self.frodo_team.members.add(self.gandalf)

        self.bilbo_team = Team.objects.create(
            name="Bilbo Team",
        )
        self.bilbo_team.members.add(self.bilbo)
        self.bilbo_team.members.add(self.aragorn)
        self.bilbo_team.members.add(self.gandalf)

        self.gandalf_team = Team.objects.create(
            name="Gandalf Team",
        )
        self.gandalf_team.members.add(self.aragorn)
        self.gandalf_team.members.add(self.gandalf)

    def test_auto_add_auth_user_to_team(self):
        self.client.force_login(self.frodo)
        form_data = {
            "name": "The Fellowship",
            "description": "One team to rule them all",
            "members": [
                self.bilbo.id,
                self.gandalf.id,
            ]
        }
        response = self.client.post(
            reverse("tasks:team-create"),
            data=form_data,
        )
        self.assertEqual(response.status_code, 302)
        created_team = Team.objects.filter(name="The Fellowship").first()
        self.assertIsNotNone(created_team)
        self.assertEqual(created_team.members.count(), 3)
        self.assertIn(self.frodo, created_team.members.all())

    def test_team_queryset_for_auth_user(self):
        self.client.force_login(self.frodo)
        response = self.client.get(reverse("tasks:team-list"))
        teams = response.context["team_list"]
        self.assertEqual(len(teams), 1)
        self.assertEqual(teams[0].name, "Frodo Team")

    def test_leave_team(self):
        self.client.force_login(self.frodo)

        response = self.client.post(
            reverse(
                "tasks:team-leave",
                kwargs={"pk": self.frodo_team.id}
            ),
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Team.objects.filter(name="Frodo Team").exists())
        self.frodo_team.refresh_from_db()
        self.assertNotIn(self.frodo, self.frodo_team.members.all())
        self.assertEqual(self.frodo_team.members.count(), 1)
        self.assertIn(self.gandalf, self.frodo_team.members.all())

    def test_leave_button_display_for_more_than_one_member_in_a_team(self):
        self.client.force_login(self.frodo)
        url = reverse("tasks:team-update", kwargs={"pk": self.frodo_team.id})
        response = self.client.get(url)
        leave_url = reverse("tasks:team-leave", kwargs={"pk": self.frodo_team.id})
        delete_url = reverse("tasks:team-delete", kwargs={"pk": self.frodo_team.id})
        self.assertContains(response, leave_url)
        self.assertNotContains(response, delete_url)

    def test_delete_button_display_for_only_last_member_in_a_team(self):
        self.client.force_login(self.frodo)
        self.frodo_team.members.remove(self.gandalf)
        url = reverse("tasks:team-update", kwargs={"pk": self.frodo_team.id})
        response = self.client.get(url)
        leave_url = reverse("tasks:team-leave", kwargs={"pk": self.frodo_team.id})
        delete_url = reverse("tasks:team-delete", kwargs={"pk": self.frodo_team.id})
        self.assertContains(response, delete_url)
        self.assertNotContains(response, leave_url)
