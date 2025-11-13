
# traditional-bands-email

Lightweight utility to run a SQL query, summarize results, and email a styled HTML report. Intended to query a SQL Server database, build a summary row for locations, and deliver the results as an HTML email.

**Project status:** Minimal working scripts — add environment variables and an ODBC driver to run in your environment.

**Quick Start**

- **Clone:** `git clone <repo>`
- **Create venv:** `python -m venv .venv`
- **Activate (PowerShell):** `.\.venv\Scripts\Activate.ps1`
- **Install:** `pip install -r requirements.txt` (or use `pip install -e .` / `pyproject.toml` deps)

**Run**

- From repository root: `python -m src.main`
- Or: run the provided batch helper: `run_script.bat` (Windows)

**What it does**

- Runs the SQL in `sql_query/traditional_bands_shipDate_group.sql` against a SQL Server database.
- Loads the result into a pandas `DataFrame` (`src/db_handler.py`).
- Produces a one-row summary of numeric columns (excluding the first column) using `src/py_handler.py`.
- Sends an HTML+plain-text email containing the summary and raw grouped results using `src/email_handler.py`.

**Files Overview**

- `src/main.py`: orchestration script — locates the SQL file, executes the pipeline, and triggers email.
- `src/db_handler.py`: reads the SQL file, connects to SQL Server via `pyodbc`, and returns a pandas DataFrame.
- `src/py_handler.py`: contains `location_sum_row()` which sums numeric columns (excluding first column) into a one-row DataFrame.
- `src/email_handler.py`: converts DataFrames to HTML tables and sends email via SMTP.
- `sql_query/traditional_bands_shipDate_group.sql`: the SQL query used by `src/main.py`.

**Environment / Configuration**

Create a `.env` in the project root (or set environment variables in your system) with the following keys:

- `SQL_SERVER` — SQL Server hostname or IP
- `SQL_DATABASE` — database name
- `SQL_USERNAME` — DB username
- `SQL_PASSWORD` — DB password
- `EMAIL_SMTP_USER` — SMTP username (often your email)
- `EMAIL_SMTP_PASS` — SMTP password or app password
- `EMAIL_FROM` (optional) — the from address for outgoing emails
- Optional SMTP overrides: `EMAIL_SMTP_SERVER`, `EMAIL_SMTP_PORT`

Notes:
- `src/db_handler.py` uses `ODBC Driver 17 for SQL Server` by default. Install the appropriate ODBC driver for your OS or change the driver string in `src/db_handler.py`.
- For Gmail SMTP, consider using an app password and ensure the account allows SMTP access.

**Dependencies**

Key dependencies are declared in `pyproject.toml`. At a minimum this project uses:

- `pandas` — data handling
- `pyodbc` — SQL Server connection
- `python-dotenv` (`dotenv`) — load `.env` files

If you prefer a `requirements.txt`, you can generate one from your environment with `pip freeze > requirements.txt`.

**Usage Tips & Troubleshooting**

- SQL file path: `src/main.py` expects the SQL file at `sql_query/traditional_bands_shipDate_group.sql` relative to the project root. Keep the path or update `src/main.py` accordingly.
- If the DataFrame returned is empty, `src/main.py` prints a message and stops — verify the query and DB creds.
- SMTP login errors indicate wrong credentials, blocked ports, or provider restrictions (use app passwords where required).
- ODBC / `pyodbc` errors often mean the driver is missing or the connection string is incorrect. Adjust the `driver` variable in `src/db_handler.py`.

**Development**

- Run the main pipeline locally: `python -m src.main`
- To test email sending without hitting SMTP, consider using a local SMTP debug server: `python -m smtpd -c DebuggingServer -n localhost:1025` and set `EMAIL_SMTP_SERVER=localhost` and `EMAIL_SMTP_PORT=1025` in `.env`.

**Contact / Attribution**

Created and maintained in repo `traditional_bands_email`.

---

If you'd like, I can also:

- add a `requirements.txt` generated from `pyproject.toml` deps,
- add a small `.env.example` file with the variable names,
- or create a GitHub Actions workflow to run the script on a schedule.
