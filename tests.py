import os
import tempfile
import unittest

TEST_DB = os.path.join(tempfile.gettempdir(), "test_foundation.db")
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
os.environ["FOUNDATION_DB"] = TEST_DB

import app as app_module

PUBLIC_PAGES = ["/", "/about", "/initiatives", "/trustees", "/events", "/contact"]
ADMIN_PAGES = ["/admin", "/admin/trustees", "/admin/trustees/new", "/admin/events", "/admin/events/new", "/admin/messages"]


class FoundationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app_module.db.init_db()

    def setUp(self):
        self.client = app_module.app.test_client()

    def scalar(self, sql, args=()):
        with app_module.app.app_context():
            return app_module.db.scalar(sql, args)

    def test_public_pages_load(self):
        for page in PUBLIC_PAGES:
            with self.subTest(page=page):
                self.assertEqual(self.client.get(page).status_code, 200)

    def test_admin_pages_load(self):
        for page in ADMIN_PAGES:
            with self.subTest(page=page):
                self.assertEqual(self.client.get(page).status_code, 200)

    def test_homepage_shows_mission_and_seed_events(self):
        body = self.client.get("/").get_data(as_text=True)
        self.assertIn("Michael Emeakayi", body)
        self.assertIn("Our mission", body)
        self.assertIn("Annual Harvest", body)

    def test_trustees_page_shows_seed_trustees(self):
        body = self.client.get("/trustees").get_data(as_text=True)
        self.assertIn("Founder &amp; Chairperson", body)
        self.assertIn("Hope Chizoba Emeakayi Okafor", body)

    def test_contact_form_saves_message(self):
        response = self.client.post("/contact", data={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "subject": "Volunteering",
            "message": "I would like to volunteer.",
        }, follow_redirects=True)
        self.assertIn("Thank you", response.get_data(as_text=True))
        count = self.scalar("SELECT COUNT(*) FROM messages")
        self.assertEqual(count, 1)

    def test_contact_form_requires_fields(self):
        response = self.client.post("/contact", data={
            "name": "", "email": "", "subject": "", "message": "",
        }, follow_redirects=True)
        self.assertIn("Please fill in", response.get_data(as_text=True))
        count = self.scalar("SELECT COUNT(*) FROM messages")
        self.assertEqual(count, 0)

    def test_add_edit_delete_trustee(self):
        response = self.client.post("/admin/trustees/new", data={
            "name": "Test Person", "role": "Treasurer", "bio": "Bio",
        }, follow_redirects=True)
        self.assertIn("Test Person", response.get_data(as_text=True))
        tid = self.scalar("SELECT id FROM trustees WHERE name = ?", ("Test Person",))

        response = self.client.post(f"/admin/trustees/{tid}/edit", data={
            "name": "Test Person", "role": "Chairperson", "bio": "Updated",
        }, follow_redirects=True)
        self.assertIn("Chairperson", response.get_data(as_text=True))

        self.client.post(f"/admin/trustees/{tid}/delete")
        count = self.scalar("SELECT COUNT(*) FROM trustees WHERE id = ?", (tid,))
        self.assertEqual(count, 0)

    def test_add_edit_delete_event(self):
        self.client.post("/admin/events/new", data={
            "title": "Test Event", "date": "2026-12-05", "location": "Enugu",
            "description": "Desc",
        }, follow_redirects=True)
        eid = self.scalar("SELECT id FROM events WHERE title = ?", ("Test Event",))
        self.assertIsNotNone(eid)

        response = self.client.post(f"/admin/events/{eid}/edit", data={
            "title": "Test Event", "date": "2026-12-06", "location": "Enugu",
            "description": "Updated",
        }, follow_redirects=True)
        self.assertIn("2026-12-06", response.get_data(as_text=True))

        self.client.post(f"/admin/events/{eid}/delete")
        count = self.scalar("SELECT COUNT(*) FROM events WHERE id = ?", (eid,))
        self.assertEqual(count, 0)

    def test_unknown_trustee_edit_returns_404(self):
        response = self.client.get("/admin/trustees/99999/edit")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)