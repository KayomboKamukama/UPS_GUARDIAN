# UPS Guardian

**Subtitle:** Lightweight Central UPS Monitoring for Multi-Station ICT Environments.

UPS Guardian is an open-source, Windows-first desktop tool focused specifically on UPS and power monitoring.

## Phase 1 Status (Implemented)
- Modern PySide6 desktop shell (Dashboard, Devices, Alerts, Reports, Settings, About)
- SQLite local database with UPS-focused schema
- UPS inventory CRUD with CSV import/export
- Naming convention validator + auto-generator
- OID profile foundation with JSON profiles and required-key validation
- Mock polling engine with realistic UPS telemetry
- Alert rules engine with deduplication/escalation, acknowledgement, and comments
- CSV exports for inventory, active alerts, and latest status summary
- PyInstaller-ready Windows packaging assets

## Quick Start
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
python -m ups_guardian.main
```

## Configuration
- Primary config file: `config/app_config.json`
- OID profiles: `profiles/*.json`
- Seed inventory: `config/sample_devices.csv`

## Windows Build
```bat
scripts\build_windows.bat
```
or
```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

## Screenshots
- Placeholder: add desktop screenshots of Dashboard/Devices/Alerts once captured on a GUI-enabled Windows environment.

## License
MIT (`LICENSE`).
