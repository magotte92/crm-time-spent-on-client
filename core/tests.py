import shutil
import tempfile
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import RequestFactory, TestCase
from django.urls import reverse

from core.models import ClientModel, Clientele, SubTask, Task
from employee.views import (
    AllClientsPageView,
    AllTaskPage,
    EmployeeTabPageView,
    SumOfClientView,
)


class ProjectSmokeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("recorder", password="test-pass-123")
        self.clientele = Clientele.objects.create(name="ACME")
        self.task = Task.objects.create(task="Filing")
        self.subtask = SubTask.objects.create(mother_task=self.task, subtask="Forms")
        self.stuff = Path("stuff")
        self.backup = Path(tempfile.mkdtemp())
        if self.stuff.exists():
            shutil.copytree(self.stuff, self.backup / "stuff")

    def tearDown(self):
        if self.stuff.exists():
            shutil.rmtree(self.stuff)
        backed_up = self.backup / "stuff"
        if backed_up.exists():
            shutil.copytree(backed_up, self.stuff)
        shutil.rmtree(self.backup)

    def test_django_check(self):
        call_command("check")

    def test_login_page_renders(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_recorder_requires_login(self):
        response = self.client.get(reverse("recorder"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_record_time_and_autocomplete(self):
        self.client.login(username="recorder", password="test-pass-123")
        page = self.client.get(reverse("recorder"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Forms")

        created = self.client.post(
            reverse("recorder"),
            {
                "name": self.clientele.pk,
                "subtask": self.subtask.pk,
                "time_spent": "30",
            },
        )
        self.assertEqual(created.status_code, 302, getattr(created, "content", b""))
        record = ClientModel.objects.get()
        self.assertEqual(record.name, self.clientele)
        self.assertEqual(record.subtask, self.subtask)
        self.assertEqual(record.task, self.task)
        self.assertEqual(record.time_spent, "30")
        self.assertEqual(record.dec_name, "recorder")

        suggestions = self.client.get(reverse("name-autocomplete"), {"q": "AC"})
        self.assertEqual(suggestions.status_code, 200)
        self.assertContains(suggestions, "ACME")

    def test_logout_accepts_post_only(self):
        self.client.login(username="recorder", password="test-pass-123")
        rejected = self.client.get("/accounts/logout/")
        self.assertEqual(rejected.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

        logged_out = self.client.post("/accounts/logout/")
        self.assertEqual(logged_out.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_report_views_aggregate_minutes(self):
        ClientModel.objects.create(
            name=self.clientele,
            time_spent="90",
            dec_name="recorder",
            task=self.task,
            subtask=self.subtask,
        )
        request = RequestFactory().get("/")
        request.user = self.user

        clients = AllClientsPageView()
        clients.setup(request)
        client_rows = list(clients.get_context_data()["df"])
        self.assertEqual(len(client_rows), 1)
        self.assertEqual(client_rows[0][0], "ACME")
        self.assertEqual(client_rows[0][1], "Filing")
        self.assertEqual(client_rows[0][2], "Forms")
        self.assertEqual(str(client_rows[0][3]), "0 days 01:30:00")

        totals = SumOfClientView()
        totals.setup(request)
        total_rows = list(totals.get_context_data()["df"])
        self.assertEqual(total_rows[0][0], "ACME")
        self.assertEqual(str(total_rows[0][1]), "0 days 01:30:00")

        tasks = AllTaskPage()
        tasks.setup(request)
        task_rows = list(tasks.get_context_data()["df"])
        self.assertEqual(task_rows[0][0], "Filing")
        self.assertEqual(task_rows[0][1], "Forms")
        self.assertEqual(task_rows[0][2], "01:30")

        employees = EmployeeTabPageView()
        employees.setup(request)
        employee_rows = list(employees.get_context_data()["df"])
        self.assertEqual(employee_rows[0][0], "recorder")
        self.assertEqual(employee_rows[0][2], "01:30")
