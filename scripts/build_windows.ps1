param(
    [switch]$Portable
)

Write-Host "Building UPS Guardian executable with PyInstaller..."
python -m PyInstaller --clean --noconfirm build/ups_guardian.spec

if ($Portable) {
    Write-Host "Portable build generated in dist/UPSGuardian/"
}
else {
    Write-Host "Standard build generated in dist/"
}
