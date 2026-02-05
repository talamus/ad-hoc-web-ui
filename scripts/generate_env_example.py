#!/usr/bin/env python3
"""Generate .env.example from Settings model."""

import sys
from pathlib import Path

# Add project root to path to import app modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from web.settings import ROOT_PATH, Settings  # noqa: E402


def generate_env_example() -> str:
    """Generate .env.example content from Settings field definitions."""
    lines = ["# Configuration for Ad Hoc Web UI", "# Copy to .env and modify as needed", ""]

    for name, field_info in Settings.model_fields.items():
        description = field_info.description or ""
        default = field_info.default

        # Format default value, make paths relative to project root
        if isinstance(default, Path):
            default_str = str(default).replace(str(ROOT_PATH), ".")
        elif default is None:
            default_str = ""
        else:
            default_str = str(default)

        lines.append(f"# {description}")
        lines.append(f"# {name.upper()}={default_str}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Print .env.example content to stdout."""
    print(generate_env_example())


if __name__ == "__main__":
    main()
