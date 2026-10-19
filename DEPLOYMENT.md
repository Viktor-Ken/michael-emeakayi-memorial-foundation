# Deploying to PythonAnywhere (free)

This site works well on the PythonAnywhere free tier: you get a free
`https://YOUR-USERNAME.pythonanywhere.com` subdomain, Flask runs natively, and the
SQLite database (`foundation.db`) persists between restarts.

The database is created and seeded automatically on the first request, so there is
no manual setup step after the code is in place.

## 1. One-time local prep

Generate a secret key to use as an environment variable on the server (step 7):

```bash
python -c "import secrets; print(secrets.token_hex(24))"
```

The secret key output goes in the `SECRET_KEY` variable. It does not need to be
committed to the repository.

## 2. Create an account

1. Sign up at https://www.pythonanywhere.com (free, no card required).
2. Note your username — it becomes your subdomain (`https://YOUR-USERNAME.pythonanywhere.com`).

## 3. Get the code onto PythonAnywhere

Open the **Consoles** tab and start a **Bash** console, then clone the repository:

```bash
cd ~
git clone https://github.com/Viktor-Ken/michael-emeakayi-memorial-foundation.git
```

The project now lives at `~/michael-emeakayi-memorial-foundation`.

Alternatively, use the **Files** tab to upload `app.py`, `db.py`, `schema.sql`,
`seed.sql`, `tests.py`, `requirements.txt`, and the `templates/` and `static/`
folders into a `mysite` folder.

## 4. Create a virtualenv and install dependencies

In the same Bash console:

```bash
mkvirtualenv foundation --python=python3.10
pip install -r ~/michael-emeakayi-memorial-foundation/requirements.txt
```

Note the virtualenv name (`foundation`); you will point the web app at it in the next step.

## 5. Create the web app

1. Go to the **Web** tab.
2. Click **Add a new web app**.
3. Choose **Manual configuration** (not their Flask wizard), pick Python 3.10.
4. Under **Virtualenv**, enter:
   ```
   /home/YOUR-USERNAME/.virtualenvs/foundation
   ```
5. Under **Code - Working directory**, enter:
   ```
   /home/YOUR-USERNAME/michael-emeakayi-memorial-foundation
   ```

## 6. Configure static files

Under **Static files**, add:

- **URL**: `/static/`
- **Directory**: `/home/YOUR-USERNAME/michael-emeakayi-memorial-foundation/static`

This is required for the CSS to load.

## 7. Set the secret key

On the **Web** tab, under **Environment variables**, add:

```
SECRET_KEY=copy-a-long-random-string-here
SECURE_COOKIES=1
```

If your plan does not show that section, edit the `SECRET_KEY` value directly at the
top of `/home/YOUR-USERNAME/michael-emeakayi-memorial-foundation/app.py`.

Without it the app falls back to a placeholder value.

## 8. Point the WSGI file at our app

Under **Code**, click the link for the **WSGI configuration file**
(`/var/www/YOUR-USERNAME_pythonanywhere_com_wsgi.py`) and replace its contents with:

```python
import sys

project_home = '/home/YOUR-USERNAME/michael-emeakayi-memorial-foundation'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import app as application
```

Save the file.

## 9. Reload and verify

Back on the **Web** tab, click the green **Reload** button. Then visit:

- `https://YOUR-USERNAME.pythonanywhere.com` — homepage
- `https://YOUR-USERNAME.pythonanywhere.com/admin` — content management (no password yet; keep this URL private)
- `https://YOUR-USERNAME.pythonanywhere.com/static/css/style.css` — confirms static files work

## Updating the site later

In a Bash console:

```bash
cd ~/michael-emeakayi-memorial-foundation
git pull
```

Then click **Reload** on the Web tab. Your data in `foundation.db` is kept.

## Troubleshooting

- **Broken styles** — check the static files mapping in step 6 is exact (trailing `/`).
- **Error 500 on first load** — the database is created on first request; waiting a
  few seconds then reloading usually resolves it. If not, check the error log linked on
  the Web tab.
- **Ports/bind** — none needed; PythonAnywhere ignores `app.run()` and serves the app
  through the WSGI file.
- **`debug=True`** — irrelevant in production; when served via WSGI the
  `if __name__ == "__main__"` block in `app.py` never runs.

## When you are ready for a custom domain

PythonAnywhere charges a small fee to attach your own domain. If you prefer to host
your own domain free elsewhere later, Render and Railway also run Flask, but note both
use an ephemeral filesystem on their free tiers — your SQLite data would reset on each
deploy unless you move to a database service like PostgreSQL.