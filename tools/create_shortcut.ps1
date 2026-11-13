# Creates "Bomberman" shortcuts on the Desktop and in the Start menu.
# Called by INSTALL_SHORTCUT.bat, which finds pythonw.exe and passes it in.
param([Parameter(Mandatory = $true)][string]$PythonW)

$root = Split-Path -Parent $PSScriptRoot
$launcher = Join-Path $root "Bomberman.pyw"
$icon = Join-Path $root "assets\bomberman.ico"
$log = Join-Path $root "shortcut_install.log"
"PythonW: $PythonW" | Set-Content -Encoding UTF8 $log

$places = @(
    [Environment]::GetFolderPath("Desktop"),
    [Environment]::GetFolderPath("Programs")
)
$created = 0
$shell = New-Object -ComObject WScript.Shell
foreach ($dir in $places) {
    if (-not $dir) { continue }
    $path = Join-Path $dir "Bomberman.lnk"
    try {
        # WScript.Shell cannot save to some non-ASCII paths (e.g. a Hebrew
        # OneDrive Desktop), so build the shortcut in TEMP and move it.
        $tmp = Join-Path $env:TEMP ("bomberman_" + [guid]::NewGuid().ToString("N") + ".lnk")
        $link = $shell.CreateShortcut($tmp)
        $link.TargetPath = $PythonW
        $link.Arguments = '"' + $launcher + '"'
        $link.WorkingDirectory = $root
        $link.IconLocation = $icon + ",0"
        $link.Description = "Bomberman - software engineering project"
        $link.Save()
        Move-Item -LiteralPath $tmp -Destination $path -Force
        $created++
        Write-Host "Created: $path"
        "Created: $path" | Add-Content -Encoding UTF8 $log
    } catch {
        Write-Host "Error: $_"
        "Error ($dir): $_" | Add-Content -Encoding UTF8 $log
    }
}
if ($created -eq 0) { exit 1 }
