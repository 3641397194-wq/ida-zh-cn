<#
  Renders the README artwork (assets\*.png) from the HTML pages in this folder using headless Edge/Chrome.
  Usage:  powershell -ExecutionPolicy Bypass -File tools\design\build.ps1
#>
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$out  = Join-Path (Split-Path -Parent (Split-Path -Parent $here)) 'assets'
New-Item -ItemType Directory -Force -Path $out | Out-Null

$candidates = @(
  "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
  "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
)
$browser = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $browser) { throw 'Edge or Chrome not found' }

# page, output name, width, height, device scale factor
$pages = @(
  @('banner',          'banner',          1600, 520, 2),
  @('social',          'social-preview',  1280, 640, 1),
  @('compare-main',    'compare-main',    1600, 690, 2),
  @('compare-menus',   'compare-menus',   1600, 640, 2),
  @('compare-dialog',  'compare-dialog',  1600, 720, 2)
)

$profile = Join-Path $env:TEMP 'ida-zh-cn-design-profile'
foreach ($p in $pages) {
  $src = 'file:///' + ((Join-Path $here ($p[0] + '.html')) -replace '\\', '/')
  $dst = Join-Path $out ($p[1] + '.png')
  $args = @('--headless=new', '--disable-gpu', '--hide-scrollbars', "--force-device-scale-factor=$($p[4])",
            "--user-data-dir=$profile", "--window-size=$($p[2]),$($p[3])", '--virtual-time-budget=4000',
            "--screenshot=$dst", $src)
  Start-Process -FilePath $browser -ArgumentList $args -Wait -WindowStyle Hidden | Out-Null
  '{0,-16} -> {1}' -f $p[0], $dst
}
