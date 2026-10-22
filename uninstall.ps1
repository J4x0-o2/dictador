# Dictador uninstaller.
# Usage: irm https://raw.githubusercontent.com/J4x0-o2/dictador/main/uninstall.ps1 | iex

$installDir = Join-Path $env:LOCALAPPDATA "Dictador"

Get-CimInstance Win32_Process -Filter "Name like 'python%'" |
    Where-Object { $_.CommandLine -like "*$installDir*" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

foreach ($dir in @([Environment]::GetFolderPath("Startup"), [Environment]::GetFolderPath("Programs"))) {
    Remove-Item (Join-Path $dir "Dictador.lnk") -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 1  # let the process release its files
Remove-Item $installDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Dictador desinstalado. Los modelos descargados quedan en ~\.cache\huggingface (podés borrarlos a mano)." -ForegroundColor Green
