# Daudu Mezenobe Andrew — Portfolio

Production Django portfolio site for a Full-Stack Python Developer.

## Stack

Django · PostgreSQL · Bootstrap · Render

## Local setup

1. Copy the environment file and fill in real values:

   **macOS / Linux:**
   ```bash
   cp .env.example .env
   ```

   **Windows (PowerShell):**
   ```powershell
   Copy-Item .env.example .env
   ```

2. Start a local Postgres instance (matches production exactly):

   ```bash
   docker compose up -d db
   ```

3. Create a virtual environment and install dependencies:

   **macOS / Linux:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-dev.txt
   ```

   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements-dev.txt
   ```
   If PowerShell blocks the activation script with an execution-policy error, run
   `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first, then retry.

4. Run migrations and the test suite:

   ```bash
   python manage.py migrate
   python manage.py test
   ```

5. Start the dev server:

   ```bash
   python manage.py runserver
   ```

6. Confirm the database connection is live:

   **macOS / Linux:**
   ```bash
   curl http://localhost:8000/healthz/
   # {"status": "ok"}
   ```

   **Windows (PowerShell):**
   ```powershell
   Invoke-RestMethod http://localhost:8000/healthz/
   # status
   # ------
   # ok
   ```

## Linting

```bash
ruff check .
```
