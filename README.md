# Ad Hoc web UI for creating throwaway servers

## Quick Start

```bash
# Create virtual environment and download dependencies
uv sync

# Create an admin user
uv run python scripts/create_admin.py --username admin --password yourpassword

# Run the application
uv run python run.py
```

Then visit http://localhost:8000 and log in with your credentials.

## Project Structure

```
ad-hoc-creator/
├── run.py              # Application entry point
├── scripts/            # Utility scripts
│   └── create_admin.py
├── app/                # Main application package
│   ├── main.py        # FastAPI app setup
│   ├── config.py      # Configuration
│   ├── database.py    # Database models
│   ├── auth.py        # Authentication
│   ├── routes/        # API and page routes
│   ├── templates/     # Jinja2 templates
│   └── static/        # CSS and JavaScript
└── docs/              # Documentation
    ├── PLAN.md
    └── GETTING_STARTED.md
```

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup and usage instructions.
