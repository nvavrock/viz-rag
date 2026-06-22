"""Runtime checks for viz-rag entry points (Windows venv / PATH guard)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"


def in_project_venv() -> bool:
    return sys.prefix != sys.base_prefix


def ensure_project_venv(module: str) -> None:
    """Block system Python when project .venv exists (Windows activate.ps1 often fails)."""
    in_venv = in_project_venv()
    venv_exists = VENV_PYTHON.is_file()

    if not in_venv and venv_exists:
        suggested = f".venv\\Scripts\\python.exe -m {module}"
        print(
            "Error: viz-rag dependencies are in the project .venv, but you ran:\n"
            f"  {sys.executable}\n\n"
            "Use one of these (no PowerShell activate needed):\n"
            f"  {suggested}\n"
            f"  .\\scripts\\run.cmd -m {module}\n"
            f"  .\\scripts\\run.ps1 -m {module}   (may be blocked by ExecutionPolicy; use run.cmd)\n",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        import langchain_chroma  # noqa: F401
    except ModuleNotFoundError as exc:
        if venv_exists and not in_venv:
            print(
                f"ModuleNotFoundError: {exc}\n"
                "Use the project venv Python (see commands above).",
                file=sys.stderr,
            )
            sys.exit(1)
        print(
            f"ModuleNotFoundError: {exc}\n"
            "Install dependencies:\n"
            f"  {VENV_PYTHON if venv_exists else 'python'} -m pip install -e .",
            file=sys.stderr,
        )
        sys.exit(1)
