# CoC Bot Prerequisites Installer for Windows
# Run this script in PowerShell to set up everything automatically.

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "     CoC Bot - Windows Installer         " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 0. Windows Server check (Install Wireless LAN Service for wlanapi.dll)
try {
    $os = Get-CimInstance Win32_OperatingSystem
    if ($os.ProductType -ne 1) {
        Write-Host "Windows Server erkannt. Pruefe Wireless LAN Service (wlanapi.dll)..." -ForegroundColor Yellow
        $feature = Get-WindowsFeature -Name Wireless-Networking -ErrorAction SilentlyContinue
        if ($feature -and -not $feature.Installed) {
            Write-Host "Installiere Wireless-Networking Feature (benoetigt Administratorrechte)..." -ForegroundColor Yellow
            Install-WindowsFeature -Name Wireless-Networking -ErrorAction Stop
            Write-Host "Feature erfolgreich installiert! Bitte starte Windows neu, damit ADB funktioniert." -ForegroundColor Green
        } else {
            Write-Host "Wireless-Networking Feature ist bereits installiert." -ForegroundColor Green
        }
    }
} catch {
    Write-Warning "Konnte Windows Server Features nicht pruefen. Stelle sicher, dass du als Administrator angemeldet bist, falls wlanapi.dll Fehler auftreten."
}

# 1. Check Python installation
Write-Host "[1/6] Pruefe Python-Installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Gefunden: $pythonVersion" -ForegroundColor Green
    if ($pythonVersion -match 'Python (\d+)\.(\d+)') {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
            Write-Warning "Python 3.11 oder hoeher wird empfohlen! Deine Version ist eventuell veraltet."
        }
    }
} catch {
    Write-Error "Python wurde nicht gefunden! Bitte installiere Python 3.11+ und aktiviere 'Add python.exe to PATH'."
    Exit
}

# 2. Setup ADB (Android Debug Bridge)
Write-Host ""
Write-Host "[2/6] Richte Android Debug Bridge (ADB) ein..." -ForegroundColor Yellow
$appDataDir = Join-Path $HOME ".CoC_Bot"
if (-not (Test-Path $appDataDir)) {
    New-Item -ItemType Directory -Path $appDataDir | Out-Null
}
$adbDir = Join-Path $appDataDir "platform-tools"
$zipFile = Join-Path $appDataDir "platform-tools.zip"

if (Test-Path (Join-Path $adbDir "adb.exe")) {
    Write-Host "ADB ist bereits unter $adbDir installiert." -ForegroundColor Green
} else {
    Write-Host "Lade Google Platform-Tools (ADB) herunter..." -ForegroundColor Gray
    $url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
    Invoke-WebRequest -Uri $url -OutFile $zipFile
    
    Write-Host "Entpacke ADB..." -ForegroundColor Gray
    Expand-Archive -Path $zipFile -DestinationPath $appDataDir -Force
    Remove-Item $zipFile
    Write-Host "ADB erfolgreich nach $adbDir installiert." -ForegroundColor Green
}

# 3. Add ADB to User PATH Environment Variable
Write-Host ""
Write-Host "[3/6] Fuege ADB zum Windows-Benutzerpfad (PATH) hinzu..." -ForegroundColor Yellow
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -like "*$adbDir*") {
    Write-Host "ADB befindet sich bereits in deinem PATH." -ForegroundColor Green
} else {
    Write-Host "Fuege $adbDir zum User PATH hinzu..." -ForegroundColor Gray
    $newPath = "$userPath;$adbDir"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    # Update current session PATH too
    $env:PATH = "$env:PATH;$adbDir"
    Write-Host "PATH erfolgreich aktualisiert! (Aenderungen gelten fuer neue Eingabeaufforderungen)." -ForegroundColor Green
}

# 4. Create virtual environment and install requirements
Write-Host ""
Write-Host "[4/6] Erstelle Python virtuelle Umgebung (.venv) und installiere Bibliotheken..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    Write-Host "Erstelle .venv..." -ForegroundColor Gray
    python -m venv .venv
}

$venvPython = ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Error "Virtuelle Umgebung (.venv) konnte nicht erstellt werden."
    Exit
}

Write-Host "Upgrade pip..." -ForegroundColor Gray
Start-Process -FilePath $venvPython -ArgumentList "-m pip install --upgrade pip" -Wait -NoNewWindow

Write-Host "Installiere Bot-Abhaengigkeiten..." -ForegroundColor Gray
Start-Process -FilePath $venvPython -ArgumentList "-m pip install -r src/requirements.txt" -Wait -NoNewWindow

Write-Host "Installiere Web-App-Abhaengigkeiten..." -ForegroundColor Gray
Start-Process -FilePath $venvPython -ArgumentList "-m pip install -r app/requirements.txt" -Wait -NoNewWindow

Write-Host "Abhaengigkeiten erfolgreich installiert!" -ForegroundColor Green

# 5. Create configs.py if not exists
Write-Host ""
Write-Host "[5/6] Konfigurationsdateien einrichten..." -ForegroundColor Yellow
if (-not (Test-Path "src/configs.py")) {
    Copy-Item "src/configs.template.py" "src/configs.py"
    Write-Host "src/configs.py aus Template erstellt. Bitte passe deine Passwoerter dort an!" -ForegroundColor Green
} else {
    Write-Host "src/configs.py existiert bereits (uebersprungen)." -ForegroundColor Gray
}

# 6. BlueStacks check
Write-Host ""
Write-Host "[6/6] BlueStacks Setup..." -ForegroundColor Yellow
Write-Host "BlueStacks 5 muss manuell installiert werden." -ForegroundColor Gray
$choice = Read-Host "Moechtest du die offizielle BlueStacks Download-Seite im Browser oeffnen? (y/n)"
if ($choice.ToLower() -eq 'y') {
    Start-Process "https://www.bluestacks.com/download.html"
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "   SETUP ERFOLGREICH ABGESCHLOSSEN!      " -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Starte Web-Dashboard automatisch..." -ForegroundColor Yellow

# Start the Flask web app dashboard in the background (hidden window)
$appPath = Join-Path $currentDir "app\app.py"
Start-Process -FilePath $venvPython -ArgumentList $appPath -WindowStyle Hidden

# Wait briefly for server to boot, then open the browser
Start-Sleep -Seconds 2
Start-Process "http://localhost:1234"

Write-Host "Dashboard erfolgreich gestartet unter http://localhost:1234" -ForegroundColor Green
Write-Host "Viel Spass mit dem CoC Bot!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
