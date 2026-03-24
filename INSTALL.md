# INSTALL

## Requirements
- Python 3.11+
- Windows 11 target (Linux/macOS can run for development)

## Install and Run
1. Create a virtual environment.
2. Install dependencies: `pip install -e .[dev]`
3. Start app: `python -m ups_guardian.main`

## Optional: Initialize and Seed DB manually
```bash
python scripts/init_db.py
python scripts/seed_data.py
```

## Build Windows EXE
- One-folder style:
  - `scripts\build_windows.bat`
- PowerShell:
  - `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1`
