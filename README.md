# Sirene (mini IMDB-like) — Flask + MySQL

This small Flask app connects to a MySQL database named `sirene` and exposes a couple of simple endpoints for your DBMS mini project.

Quick start

1. Copy `.env.example` to `.env` and fill in your database credentials, or set the environment variables in your shell.

2. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

3. Run the app:

```powershell
# From project root
python app.py
```

Endpoints

- `GET /` — basic service info
- `GET /movies` — returns up to 100 movies from the `movies` table as JSON
- `GET /health` — checks DB connectivity

Notes and assumptions

- This project assumes a `movies` table exists in the `sirene` database with at least the columns: `id`, `title`, `year`, `genre`, `description`.
- The app reads DB credentials from environment variables: `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`. You can put them in a `.env` file and the app will load them via `python-dotenv`.
- If your schema is different, adjust the `Movie` model in `app.py`.

Troubleshooting

- If you get import errors, make sure you installed the packages in `requirements.txt` inside the active virtual environment.
- To test DB connectivity from the shell, you can run:

```powershell
# Example (PowerShell)
# install mysql client or use your preferred client
# Using Python to quick-check after installing requirements:
python -c "from sqlalchemy import create_engine; print(create_engine('mysql+pymysql://user:pass@host:3306/sirene'))"
```