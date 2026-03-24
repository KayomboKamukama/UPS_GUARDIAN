"""Application entrypoint."""

from ups_guardian.ui.app import run_app


def main() -> int:
    """Run UPS Guardian desktop application."""
    return run_app()


if __name__ == "__main__":
    raise SystemExit(main())
