# Deploying to Render

This project deploys via a Render Blueprint (`render.yaml`), committed to the
repo — the entire infrastructure is defined as code, reviewable alongside
everything else, rather than configured by hand in a dashboard.

## 1. Push to GitHub

This repo has only ever existed locally. Create a new, empty repository on
GitHub (no README, no .gitignore — this repo already has one), then:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin master
```

## 2. Create the Blueprint on Render

1. Sign in at render.com (or create an account) and connect your GitHub account.
2. Click **New > Blueprint**, select this repository.
3. Render reads `render.yaml` and shows exactly what it's about to create: one
   web service (`daudu-portfolio`) and one PostgreSQL database
   (`daudu-portfolio-db`), both on the free tier.
4. You'll be prompted to fill in a value for every secret marked `sync: false`
   in `render.yaml`:
   - `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`,
     `CONTACT_RECIPIENT_EMAIL` — your real Gmail SMTP details from Milestone 5
   - `ANTHROPIC_API_KEY` — your real key from Milestone 6
5. Click **Deploy Blueprint**.

## 3. Watch the first deploy

Render installs dependencies, runs `collectstatic`, runs `migrate`, then starts
gunicorn — watch the build log in the dashboard. The whole thing typically
takes a few minutes on the free tier.

## 4. Verify it's actually live

Once deployed:
- `https://daudu-portfolio.onrender.com/healthz/` → should print `{"status": "ok"}`
- `https://daudu-portfolio.onrender.com/` → the homepage
- `/sitemap.xml`, `/robots.txt`, `/blog/feed/` → should all still work exactly
  like they did locally

## 5. Create a superuser on the live database

Render's dashboard has a **Shell** tab for your web service — a real terminal
on the running instance:

```bash
python manage.py createsuperuser
```

Then log in at `/admin/` and add your real projects and blog posts.

## 6. Known free-tier trade-offs — accepted deliberately, not bugs

- **Cold starts**: after 15 minutes with no traffic, the service spins down.
  The next request takes 30–60 seconds to wake it back up. Upgrading to the
  Starter plan in the Render Dashboard removes this — no code changes needed.
- **30-day database expiry**: the free Postgres database is deleted 30 days
  after creation. Before that deadline, either upgrade it to a paid plan in
  the Dashboard, or export your data (`pg_dump`) and re-import after
  upgrading.

## Adding a custom domain later

Render Dashboard → your service → Settings → Custom Domains. The automatic
hostname detection in `settings.py` only covers the `onrender.com` domain —
a custom domain needs adding to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`
manually via environment variables in the Render Dashboard.
