# UPS Guardian Architecture (Phase 1)

## Final Phase 1 Architecture
- `core/`: config manager, logging config, validators, domain models
- `data/`: SQLite initialization + repositories (devices, readings, alerts, events)
- `services/`: OID profile manager, mock poller, alert rules, polling coordinator
- `ui/`: PySide6 desktop shell and UPS-focused pages/dialogs
- `config/` + `profiles/`: JSON app config, DB schema, seed inventory, OID mappings

## Notes
- Local-first, no cloud, no Docker, no web server
- Lightweight dependencies
- Mock polling abstraction ready for future real SNMP adapter replacement
- Windows packaging foundation included via PyInstaller spec and scripts
