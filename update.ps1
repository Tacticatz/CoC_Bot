# CoC Bot Updater for Windows
# Run this script in PowerShell to automatically pull the latest updates.

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "     CoC Bot - Windows Updater           " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

$currentDir = Get-Location
$gitAvailable = $false

# 1. Try to use Git first
try {
    $gitVersion = git --version 2>&1
    if ($lastExitCode -eq 0) {
        $gitAvailable = $true
    }
} catch {}

if ($gitAvailable) {
    Write-Host "[1/2] Aktualisiere via Git..." -ForegroundColor Yellow
    git pull origin main
    if ($lastExitCode -ne 0) {
        Write-Warning "Git pull fehlgeschlagen. Versuche Fallback..."
        $gitAvailable = $false
    }
}

# 2. Fallback: Download ZIP if Git is not installed/working
if (-not $gitAvailable) {
    Write-Host "[1/2] Git nicht gefunden. Lade Repository als ZIP herunter..." -ForegroundColor Yellow
    $zipUrl = "https://github.com/Tacticatz/CoC_Bot/archive/refs/heads/main.zip"
    $tempDir = Join-Path $env:TEMP "CoC_Bot_Update"
    $zipFile = Join-Path $env:TEMP "coc_bot_update.zip"

    # Clean previous temp files
    if (Test-Path $tempDir) { Remove-Item $tempDir -Recurse -Force }
    if (Test-Path $zipFile) { Remove-Item $zipFile -Force }

    try {
        # Download ZIP
        Write-Host "Lade herunter..." -ForegroundColor Gray
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile

        # Extract to temp dir
        Write-Host "Entpacke temporaere Dateien..." -ForegroundColor Gray
        Expand-Archive -Path $zipFile -DestinationPath $tempDir

        $extractedFolder = Join-Path $tempDir "CoC_Bot-main"
        if (-not (Test-Path $extractedFolder)) {
            # Find whatever folder was extracted inside temp
            $extractedFolder = Get-ChildItem $tempDir | Select-Object -First 1 | Percent-Object { $_.FullName }
        }

        Write-Host "Kopiere Dateien und bewahre Konfigurationen auf..." -ForegroundColor Gray
        # Overwrite all files, but preserve configs.py and app/data folder
        Get-ChildItem -Path $extractedFolder -Recurse | ForEach-Object {
            $destPath = $_.FullName.Replace($extractedFolder, $currentDir)
            
            # Skip user configurations and dashboard database/cache
            if ($destPath -like "*src\configs.py" -or $destPath -like "*app\data*") {
                Write-Host "Erhalte: $destPath" -ForegroundColor DarkGray
                return
            }

            if ($_.PsIsContainer) {
                if (-not (Test-Path $destPath)) {
                    New-Item -ItemType Directory -Path $destPath | Out-Null
                }
            } else {
                Copy-Item $_.FullName $destPath -Force
            }
        }
        Write-Host "Code erfolgreich aktualisiert!" -ForegroundColor Green
    } catch {
        Write-Error "Update fehlgeschlagen: $_"
        Exit
    } finally {
        # Clean up temp files
        if (Test-Path $tempDir) { Remove-Item $tempDir -Recurse -Force }
        if (Test-Path $zipFile) { Remove-Item $zipFile -Force }
    }
}

# 3. Re-install requirements
Write-Host ""
Write-Host "[2/2] Aktualisiere Python-Abhaengigkeiten..." -ForegroundColor Yellow
$venvPython = ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    Start-Process -FilePath $venvPython -ArgumentList "-m pip install -r src/requirements.txt" -Wait -NoNewWindow
    Start-Process -FilePath $venvPython -ArgumentList "-m pip install -r app/requirements.txt" -Wait -NoNewWindow
    Write-Host "Abhaengigkeiten erfolgreich aktualisiert!" -ForegroundColor Green
} else {
    Write-Warning "Keine virtuelle Umgebung (.venv) gefunden. Bitte install.ps1 ausfuehren."
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "   UPDATE ERFOLGREICH ABGESCHLOSSEN!     " -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
