param(
    [Parameter(Mandatory = $true)]
    [string]$HaConfigPath
)

$ErrorActionPreference = "Stop"

$Source = Join-Path $PSScriptRoot "custom_components\basengreen"
$Target = Join-Path $HaConfigPath "custom_components\basengreen"

if (-not (Test-Path $Source)) {
    Write-Error "Source not found: $Source"
}

$CustomComponents = Join-Path $HaConfigPath "custom_components"
if (-not (Test-Path $CustomComponents)) {
    New-Item -ItemType Directory -Path $CustomComponents -Force | Out-Null
    Write-Host "Created: $CustomComponents"
}

if (Test-Path $Target) {
    Remove-Item -Recurse -Force $Target
    Write-Host "Removed existing: $Target"
}

Copy-Item -Recurse -Force $Source $Target
Write-Host "Installed Basen Green BMS integration to:"
Write-Host "  $Target"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Restart Home Assistant"
Write-Host "  2. Settings -> Devices & services -> Add integration -> Basen Green BMS"
