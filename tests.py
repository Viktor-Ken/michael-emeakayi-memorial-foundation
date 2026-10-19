import os
import re
import tempfile
import unittest

TEST_DB = os.path.join(tempfile.gettempdir(), "test_foundation.db")
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
os.environ["FOUNDATION_DB"] = TEST_DB

import app as app_module  # noqa: E402

PUBLIC_PAGES = ["/", "/about", "/initiatives", "/trustees", "/events", "/contact"]
ADMIN_PAGES = [
    "/admin",
    "/admin/trustees",
    "/admin/trustees/new",
    "/admin/events",
    "/admin/events/new",
    "/admin/messages",
]


class FoundationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app_module.db.init_db()

    def setUp(self):
        self.client = app_module.app.test_client()
        self._csrf_token = None

    def get_csrf_token(self):
        if self._csrf_token is None:
            body = self.client.get("/contact").get_data(as_text=True)
            match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', body)
            self.assertIsNotNone(match, "csrf_token not found on /contact")
            self._csrf_token = match.group(1)
        return self._csrf_token

    def post(self, path, data=None, follow_redirects=False):
        payload = dict(data or {})
        payload.setdefault("csrf_token", self.get_csrf_token())
        return self.client.post(path, data=payload, follow_redirects=follow_redirects)

    def scalar(self, sql, args=()):
        with app_module.app.app_context():
            return app_module.db.scalar(sql, args)

    def test_public_pages_load(self):
        for page in PUBLIC_PAGES:
            with self.subTest(page=page):
                self.assertEqual(self.client.get(page).status_code, 200)

    def test_admin_pages_load_without_login(self):
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
        response = self.post("/contact", data={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "subject": "Volunteering",
            "message": "I would like to volunteer.",
        }, follow_redirects=True)
        self.assertIn("Thank you", response.get_data(as_text=True))
        count = self.scalar("SELECT COUNT(*) FROM messages")
        self.assertEqual(count, 1)

    def test_contact_form_requires_fields(self):
        before = self.scalar("SELECT COUNT(*) FROM messages")
        response = self.post("/contact", data={
            "name": "", "email": "", "subject": "", "message": "",
        }, follow_redirects=True)
        self.assertIn("Please fill in", response.get_data(as_text=True))
        count = self.scalar("SELECT COUNT(*) FROM messages")
        self.assertEqual(count, before)

    def test_contact_form_rejects_oversized_message(self):
        before = self.scalar("SELECT COUNT(*) FROM messages")
        response = self.post("/contact", data={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "subject": "Big message",
            "message": "x" * 6000,
        }, follow_redirects=True)
        self.assertIn("too long", response.get_data(as_text=True))
        count = self.scalar("SELECT COUNT(*) FROM messages")
        self.assertEqual(count, before)

    def test_contact_form_rejects_invalid_email(self):
        before = self.scalar("SELECT COUNT(*) FROM messages")
        response = self.post("/contact", data={
            "name": "Jane Doe",
            "email": "not-an-email",
            "subject": "",
            "message": "Hello",
        }, follow_redirects=True)
        self.assertIn("valid email", response.get_data(as_text=True))
        count = self.scalar("SELECT COUNT(*) FROM messages")
        self.assertEqual(count, before)

    def test_post_without_csrf_token_is_rejected(self):
        before = self.scalar("SELECT COUNT(*) FROM messages")
        response = self.client.post("/contact", data={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "subject": "",
            "message": "No token",
        })
        self.assertEqual(response.status_code, 400)
        count = self.scalar("SELECT COUNT(*) FROM messages")
        self.assertEqual(count, before)

    def test_security_headers_present(self):
        response = self.client.get("/")
        self.assertIn("Content-Security-Policy", response.headers)
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertIn("Referrer-Policy", response.headers)

    def test_custom_404_page(self):
        response = self.client.get("/donate")
        self.assertEqual(response.status_code, 404)
        self.assertIn("does not exist", response.get_data(as_text=True))

    def test_add_edit_delete_trustee(self):
        response = self.post("/admin/trustees/new", data={
            "name": "Test Person", "role": "Treasurer", "bio": "Bio",
        }, follow_redirects=True)
        self.assertIn("Test Person", response.get_data(as_text=True))
        tid = self.scalar("SELECT id FROM trustees WHERE name = ?", ("Test Person",))

        response = self.post(f"/admin/trustees/{tid}/edit", data={
            "name": "Test Person", "role": "Chairperson", "bio": "Updated",
        }, follow_redirects=True)
        self.assertIn("Chairperson", response.get_data(as_text=True))

        self.post(f"/admin/trustees/{tid}/delete")
        count = self.scalar("SELECT COUNT(*) FROM trustees WHERE id = ?", (tid,))
        self.assertEqual(count, 0)

    def test_add_edit_delete_event(self):
        self.post("/admin/events/new", data={
            "title": "Test Event", "date": "2026-12-05", "location": "Enugu",
            "description": "Desc",
        }, follow_redirects=True)
        eid = self.scalar("SELECT id FROM events WHERE title = ?", ("Test Event",))
        self.assertIsNotNone(eid)

        response = self.post(f"/admin/events/{eid}/edit", data={
            "title": "Test Event", "date": "2026-12-06", "location": "Enugu",
            "description": "Updated",
        }, follow_redirects=True)
        self.assertIn("2026-12-06", response.get_data(as_text=True))

        self.post(f"/admin/events/{eid}/delete")
        count = self.scalar("SELECT COUNT(*) FROM events WHERE id = ?", (eid,))
        self.assertEqual(count, 0)

    def test_event_form_rejects_invalid_date(self):
        response = self.post("/admin/events/new", data={
            "title": "Bad Date Event", "date": "not-a-date", "location": "",
            "description": "",
        }, follow_redirects=True)
        self.assertIn("YYYY-MM-DD", response.get_data(as_text=True))
        count = self.scalar("SELECT COUNT(*) FROM events WHERE title = ?", ("Bad Date Event",))
        self.assertEqual(count, 0)

    def test_unknown_trustee_edit_returns_404(self):
        response = self.client.get("/admin/trustees/99999/edit")
        self.assertEqual(response.status_code, 404)

    def test_backup_db_command(self):
        dest = os.path.join(tempfile.gettempdir(), "foundation-backup-test")
        with app_module.app.app_context():
            path = app_module.db.backup_db(dest)
        self.assertTrue(os.path.exists(path))
        os.remove(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
