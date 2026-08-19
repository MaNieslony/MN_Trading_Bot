# start_bot.ps1

# Change to script directory
Set-Location -Path $PSScriptRoot

# Disable Quick Edit Mode (prevents console freeze)
if ($Host.Name -eq 'ConsoleHost') {
    $mode = [Console]::TreatControlCAsInput
    [Console]::TreatControlCAsInput = $true
}

# Start the bot
python bot.py --schedule SPX-FFBPS

# Keep window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Bot exited with error code: $LASTEXITCODE" -ForegroundColor Red
    Write-Host "Press any key to close..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}