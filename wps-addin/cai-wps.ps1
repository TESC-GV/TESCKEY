param([switch]$Go)
$dst = Join-Path $env:APPDATA 'kingsoft\wps\jsaddons'
$pub = Join-Path $dst 'publish.xml'
$entry = '<jsplugin name="docso" type="et" url="docso_1.0.0" version="1.0.0" enable="enable_dev" install="null" customDomain=""/>'
New-Item -ItemType Directory -Force -Path $dst | Out-Null
if (Test-Path $pub) { Copy-Item $pub "$pub.bak" -Force; $x = Get-Content $pub -Raw -Encoding UTF8 } else { $x = '' }
$x = [regex]::Replace($x, '\s*<jsplugin[^>]*name="docso"[^>]*/>', '')
if ($Go) {
  Remove-Item -Recurse -Force (Join-Path $dst 'docso_1.0.0') -ErrorAction SilentlyContinue
  Write-Host 'Da go add-in. Mo lai WPS.'
} else {
  Copy-Item -Recurse -Force (Join-Path $PSScriptRoot 'docso_1.0.0') $dst
  if ($x -match '</jsplugins>') { $x = $x -replace '</jsplugins>', "$entry`r`n</jsplugins>" }
  else { $x = "<?xml version=`"1.0`" encoding=`"UTF-8`"?>`r`n<jsplugins>`r`n$entry`r`n</jsplugins>" }
  Write-Host 'Da cai add-in. Dong WPS roi mo lai, tim tab "So thanh chu".'
}
if ($x -match '<jsplugin') { Set-Content -Path $pub -Value $x -Encoding UTF8 } elseif (Test-Path $pub) { Set-Content -Path $pub -Value "<jsplugins>`r`n</jsplugins>" -Encoding UTF8 }
