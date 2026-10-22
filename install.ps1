# Dictador installer.
# Usage: irm https://raw.githubusercontent.com/J4x0-o2/dictador/main/install.ps1 | iex
# Optional env vars: DICTADOR_MODEL (skip the model prompt), DICTADOR_REF (branch to install).

function Install-Dictador {
    $ErrorActionPreference = "Stop"
    $ProgressPreference = "SilentlyContinue"  # Invoke-WebRequest is much faster without it

    $repo = "J4x0-o2/dictador"
    $ref = if ($env:DICTADOR_REF) { $env:DICTADOR_REF } else { "main" }
    $installDir = Join-Path $env:LOCALAPPDATA "Dictador"
    $python = Join-Path $installDir ".venv\Scripts\python.exe"
    $pythonw = Join-Path $installDir ".venv\Scripts\pythonw.exe"

    $models = @(
        @{ Name = "base";           Info = "~150 MB  - rápido, menos preciso" },
        @{ Name = "small";          Info = "~460 MB  - equilibrado (recomendado)" },
        @{ Name = "medium";         Info = "~1.5 GB  - más preciso, lento sin GPU" },
        @{ Name = "large-v3-turbo"; Info = "~1.6 GB  - el más preciso, requiere buen CPU" }
    )
    $defaultIndex = 2

    Write-Host "`n=== Instalador de Dictador ===`n" -ForegroundColor Cyan

    if ($env:DICTADOR_MODEL) {
        $model = $env:DICTADOR_MODEL
    } else {
        Write-Host "¿Qué modelo de voz querés instalar?"
        for ($i = 0; $i -lt $models.Count; $i++) {
            Write-Host ("  {0}) {1,-15} {2}" -f ($i + 1), $models[$i].Name, $models[$i].Info)
        }
        $choice = Read-Host "Elegí un número [$defaultIndex]"
        if (-not $choice) { $choice = $defaultIndex }
        if ($choice -notmatch '^\d+$' -or [int]$choice -lt 1 -or [int]$choice -gt $models.Count) {
            throw "Opción inválida: $choice"
        }
        $model = $models[[int]$choice - 1].Name
    }
    Write-Host "Modelo: $model`n"

    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Write-Host "[1/5] Instalando uv (gestor de Python)..."
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
        $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
    } else {
        Write-Host "[1/5] uv ya está instalado"
    }

    # Stop a running copy so its files can be replaced.
    Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
        Where-Object { $_.CommandLine -like "*$installDir*" } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

    Write-Host "[2/5] Descargando Dictador ($ref)..."
    $tmp = Join-Path $env:TEMP "dictador-$([guid]::NewGuid())"
    New-Item -ItemType Directory -Path $tmp | Out-Null
    $zip = Join-Path $tmp "src.zip"
    Invoke-WebRequest "https://github.com/$repo/archive/refs/heads/$ref.zip" -OutFile $zip
    Expand-Archive $zip -DestinationPath $tmp
    $src = Get-ChildItem $tmp -Directory | Select-Object -First 1
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    Copy-Item (Join-Path $src.FullName "*.py"), (Join-Path $src.FullName "requirements.txt") $installDir -Force
    Remove-Item $tmp -Recurse -Force

    Write-Host "[3/5] Instalando Python y dependencias..."
    if (-not (Test-Path $python)) { uv venv --python 3.11 (Join-Path $installDir ".venv") }
    uv pip install --python $python -r (Join-Path $installDir "requirements.txt")
    if ($LASTEXITCODE -ne 0) { throw "Falló la instalación de dependencias" }

    # Python reads this with utf-8-sig, but write it without BOM anyway.
    $config = @{ model = $model } | ConvertTo-Json
    [IO.File]::WriteAllText((Join-Path $installDir "config.json"), $config, (New-Object Text.UTF8Encoding $false))

    Write-Host "[4/5] Descargando el modelo '$model' (puede tardar varios minutos)..."
    Push-Location $installDir
    try {
        & $python -c "from faster_whisper import download_model; download_model('$model')"
        if ($LASTEXITCODE -ne 0) { throw "Falló la descarga del modelo" }
        & $python -c "from icon import make_icon; make_icon('idle', 256).save('dictador.ico')"
    } finally {
        Pop-Location
    }

    Write-Host "[5/5] Creando accesos directos..."
    $shell = New-Object -ComObject WScript.Shell
    $startup = [Environment]::GetFolderPath("Startup")
    $startMenu = [Environment]::GetFolderPath("Programs")
    foreach ($dir in @($startup, $startMenu)) {
        $lnk = $shell.CreateShortcut((Join-Path $dir "Dictador.lnk"))
        $lnk.TargetPath = $pythonw
        $lnk.Arguments = "`"$(Join-Path $installDir 'dictado.py')`""
        $lnk.WorkingDirectory = $installDir
        $lnk.IconLocation = Join-Path $installDir "dictador.ico"
        $lnk.Save()
    }

    Start-Process $pythonw -ArgumentList "`"$(Join-Path $installDir 'dictado.py')`"" -WorkingDirectory $installDir

    Write-Host "`nListo. Dictador está corriendo en la bandeja del sistema." -ForegroundColor Green
    Write-Host "  - Ctrl+Alt+Espacio para empezar/terminar de dictar"
    Write-Host "  - Arranca solo al iniciar Windows"
    Write-Host "  - Desinstalar: irm https://raw.githubusercontent.com/$repo/main/uninstall.ps1 | iex`n"
}

try {
    Install-Dictador
} catch {
    Write-Host "`nError: $_" -ForegroundColor Red
}
