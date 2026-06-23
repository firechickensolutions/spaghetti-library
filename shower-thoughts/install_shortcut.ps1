<#
.SYNOPSIS
  Install a global hotkey that launches the Shower Thoughts overlay from anywhere.

.DESCRIPTION
  Creates a Start Menu shortcut to the overlay and assigns it a global hotkey.
  Windows fires a shortcut's hotkey system-wide when the shortcut lives in the
  Start Menu (or Desktop). Everything is resolved at run time from this script's
  own location and the Python on your PATH -- no hardcoded paths.

  Windows-only (the capture stack uses WASAPI). Re-run any time to change the key.

.PARAMETER Hotkey
  The global hotkey. Windows shortcut hotkeys must be CTRL+ALT+<key>.
  Default: CTRL+ALT+T

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File install_shortcut.ps1
  powershell -ExecutionPolicy Bypass -File install_shortcut.ps1 -Hotkey "CTRL+ALT+J"
#>
param(
    [string]$Hotkey = "CTRL+ALT+T"
)
$ErrorActionPreference = 'Stop'

$repo    = $PSScriptRoot
$overlay = Join-Path $repo 'tools\capture_overlay.py'
if (-not (Test-Path $overlay)) {
    throw "Cannot find tools\capture_overlay.py next to this script ($repo). Run it from the repo root."
}

# Resolve pythonw.exe (no console window) from whatever Python is on PATH.
$pyw = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source
if (-not $pyw) {
    $py = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
    if (-not $py) { throw "No Python found on PATH. Install Python 3.11+ and re-run." }
    $pyw = Join-Path (Split-Path $py) 'pythonw.exe'
    if (-not (Test-Path $pyw)) { $pyw = $py }  # fall back to python.exe (shows a console)
}

$lnk = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Shower Thoughts.lnk'
$w = New-Object -ComObject WScript.Shell
$s = $w.CreateShortcut($lnk)
$s.TargetPath       = $pyw
$s.Arguments        = '"' + $overlay + '"'
$s.WorkingDirectory = $repo
$s.IconLocation     = 'C:\Windows\System32\imageres.dll,109'  # mic-ish icon
$s.WindowStyle      = 7
$s.Description       = 'Shower Thoughts capture overlay'
$s.Hotkey           = $Hotkey
$s.Save()

Write-Host "Installed:" $lnk
Write-Host "Launches :" $pyw $overlay
Write-Host "Hotkey   :" $s.Hotkey "(press it from anywhere)"
Write-Host ""
Write-Host "Tip: you can also pin 'Shower Thoughts' from the Start Menu to your taskbar."
