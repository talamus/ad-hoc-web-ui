# Ad Hoc web UI for creating throwaway servers

## Quick Start

```bash
# Create virtual environment and download dependencies
uv sync

# Create an admin user
uv run python scripts/create_admin.py --username admin --password yourpassword

# Start the application
./start_dev
```

Then visit <http://localhost:8000> and log in with your credentials.
