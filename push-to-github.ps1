# Run after: gh auth login
# Creates public repo and pushes main branch

$ErrorActionPreference = "Stop"
$Gh = "C:\Program Files\GitHub CLI\gh.exe"

Set-Location $PSScriptRoot

& $Gh auth status
if ($LASTEXITCODE -ne 0) {
    Write-Host "Run first: gh auth login"
    exit 1
}

& $Gh repo create BASENGREEN --public --source=. --remote=origin --description "Home Assistant integration for Basen Green batteries (Tianpower BMS via Bluetooth)" --push

Write-Host ""
Write-Host "Repository: https://github.com/papazachariakis/BASENGREEN"
