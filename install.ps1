<#
.SYNOPSIS
  Installs (or removes) the ida_zh_cn plugin for IDA Pro 9.x on Windows.

.DESCRIPTION
  Copies plugin\ida_zh_cn.py and plugin\zh_cn.json into IDA's *user* plugin directory.
  Nothing inside the IDA install directory is touched.

  Default target:  %IDAUSR%\plugins   if the IDAUSR environment variable is set,
                   %APPDATA%\Hex-Rays\IDA Pro\plugins   otherwise.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\install.ps1

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\install.ps1 -Uninstall

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\install.ps1 -Target D:\ida-user\plugins
#>
[CmdletBinding()]
param(
  [string]$Target,
  [switch]$Uninstall
)
$ErrorActionPreference = 'Stop'

if (-not $Target) {
  $Target = if ($env:IDAUSR) { Join-Path (($env:IDAUSR -split ';')[0]) 'plugins' }
            else { Join-Path $env:APPDATA 'Hex-Rays\IDA Pro\plugins' }
}

$src   = Join-Path $PSScriptRoot 'plugin'
$files = @('ida_zh_cn.py', 'zh_cn.json')

if ($Uninstall) {
  foreach ($f in $files + @('ida_zh_cn.conf.json', 'ida_zh_cn_missing.txt')) {
    $p = Join-Path $Target $f
    if (Test-Path $p) { Remove-Item $p -Force; Write-Host "removed  $p" }
  }
  Write-Host "`nUninstalled. (zh_cn_user.json, if you made one, was left in place.)"
  return
}

foreach ($f in $files) {
  if (-not (Test-Path (Join-Path $src $f))) { throw "missing $src\$f -- run this script from a full checkout" }
}

New-Item -ItemType Directory -Force -Path $Target | Out-Null
foreach ($f in $files) {
  Copy-Item (Join-Path $src $f) (Join-Path $Target $f) -Force
  Write-Host "copied   $f"
}

$script = Join-Path $Target 'ida_zh_cn.py'
Write-Host @"

Installed to: $Target

Next step -- pick one:
  1) Restart IDA. The plugin loads by itself.
  2) Without restarting: in IDA press Alt+F7 (File > Script file...) and choose
       $script

Switch back to English any time:  Edit > Plugins > "中文界面 开/关"
"@
