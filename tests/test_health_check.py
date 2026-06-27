from django.test import TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def test_healthz_confirms_database_connection(self):
        """
        Exercises the full request lifecycle end to end: URL resolution ->
        view -> database query -> JSON response. If this passes, Django,
        the URL config, and the database connection are all wired correctly.
        """
        response = self.client.get(reverse("healthz"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
