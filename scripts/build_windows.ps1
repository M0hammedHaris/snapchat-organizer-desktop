# Build script for Snapchat Organizer Desktop - Windows
# Creates a standalone folder distribution for Windows 10/11
# Run from project root: powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Snapchat Organizer Desktop - Windows Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Install Python 3.11+." -ForegroundColor Red
    exit 1
}
Write-Host "Python: $pythonVersion" -ForegroundColor Green

# Check PyInstaller
$pyiVersion = python -m PyInstaller --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    pip install "pyinstaller>=6.0.0"
}
Write-Host "PyInstaller: $(python -m PyInstaller --version)" -ForegroundColor Green
Write-Host ""

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist")  { Remove-Item -Recurse -Force "dist" }
Write-Host "Clean." -ForegroundColor Green
Write-Host ""

# Build
Write-Host "Building application..." -ForegroundColor Yellow
pyinstaller snapchat-organizer.spec --clean --noconfirm
Write-Host ""

# Verify output
$outputDir = "dist\SnapchatOrganizer"
if (-not (Test-Path $outputDir)) {
    Write-Host "ERROR: Build failed - output directory not found: $outputDir" -ForegroundColor Red
    exit 1
}

# Verify critical DLLs
$pythonDll = Get-ChildItem -Path $outputDir -Filter "python3*.dll" | Select-Object -First 1
if ($pythonDll) {
    Write-Host "python DLL: $($pythonDll.Name)" -ForegroundColor Green
} else {
    Write-Host "WARNING: python3*.dll not found in build output!" -ForegroundColor Red
}

$vcRuntime = Get-ChildItem -Path $outputDir -Filter "vcruntime*.dll" | Select-Object -First 1
if ($vcRuntime) {
    Write-Host "VC runtime: $($vcRuntime.Name)" -ForegroundColor Green
} else {
    Write-Host "WARNING: vcruntime*.dll not found - users may need VC++ Redistributable" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Build successful!" -ForegroundColor Green

# Create ZIP
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
$zipPath = "dist\Snapchat-Organizer-Windows.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath }
Compress-Archive -Path "$outputDir\*" -DestinationPath $zipPath
$zipSize = [math]::Round((Get-Item $zipPath).Length / 1MB, 1)
Write-Host "ZIP created: $zipPath ($zipSize MB)" -ForegroundColor Green
Write-Host ""

# Summary
$fileCount = (Get-ChildItem -Path $outputDir -Recurse -File).Count
$folderSize = [math]::Round((Get-ChildItem -Path $outputDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Build Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Output:  $outputDir" -ForegroundColor White
Write-Host "  Files:   $fileCount" -ForegroundColor White
Write-Host "  Size:    $folderSize MB (uncompressed)" -ForegroundColor White
Write-Host "  ZIP:     $zipPath ($zipSize MB)" -ForegroundColor White
Write-Host ""
Write-Host "To test: .\dist\SnapchatOrganizer\SnapchatOrganizer.exe" -ForegroundColor Yellow
Write-Host ""
