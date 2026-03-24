@echo off
REM Build UPS Guardian executable (Windows)
python -m PyInstaller --clean --noconfirm build\ups_guardian.spec
if %errorlevel% neq 0 (
  echo Build failed.
  exit /b %errorlevel%
)
echo Build complete. Check dist\UPSGuardian\
