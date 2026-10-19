"""Smoke checks against a running instance.

Usage: BASE_URL=http://127.0.0.1:5000 python scripts/smoke.py
"""

import os
import re
import sys
import urllib.error
import urllib.request

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000").rstrip("/")


def fetch(path):
    try:
        with urllib.request.urlopen(BASE_URL + path) as response:
            body = response.read().decode("utf-8", "replace")
            return response.status, dict(response.headers), body
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        return error.code, dict(error.headers), body


def main():
    failures = []

    def check(name, condition, detail=""):
        status = "PASS" if condition else "FAIL"
        suffix = f" — {detail}" if detail and not condition else ""
        print(f"{status}  {name}{suffix}")
        if not condition:
            failures.append(name)

    for path in ["/", "/about", "/initiatives", "/trustees", "/events", "/contact", "/admin"]:
        code, _, _ = fetch(path)
        check(f"GET {path} returns 200", code == 200, f"got {code}")

    code, _, body = fetch("/donate")
    check("GET /donate returns 404", code == 404, f"got {code}")
    check("Custom 404 page is served", "does not exist" in body)

    code, headers, _ = fetch("/")
    check("Content-Security-Policy header present", "Content-Security-Policy" in headers)
    check(
        "X-Content-Type-Options header present",
        headers.get("X-Content-Type-Options") == "nosniff",
    )
    check("X-Frame-Options header present", headers.get("X-Frame-Options") == "DENY")

    _, _, body = fetch("/contact")
    check("Contact form includes CSRF token", bool(re.search(r'name="csrf_token"', body)))

    code, _, _ = fetch("/static/css/style.css")
    check("Static CSS loads", code == 200, f"got {code}")
    code, _, _ = fetch("/static/js/main.js")
    check("Static JS loads", code == 200, f"got {code}")

    print()
    if failures:
        print(f"{len(failures)} check(s) failed.")
        sys.exit(1)
    print("All smoke checks passed.")


if __name__ == "__main__":
    main()
