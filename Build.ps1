$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonExe = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) { throw 'Crea prima .venv seguendo GUIDA.md.' }
& $pythonExe tools\build_catalog.py
if ($LASTEXITCODE -ne 0) { throw 'Catalogo non valido.' }
& $pythonExe tools\audit_scientific.py
if ($LASTEXITCODE -ne 0) { throw 'Audit numerico o dimensionale non superato.' }
& $pythonExe tools\prepare_release.py
if ($LASTEXITCODE -ne 0) { throw 'Preparazione risorse fallita.' }
$previousPath = $env:PATH
$distributionRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'dist\AtlanteFormule'))
if (-not $distributionRoot.StartsWith($PSScriptRoot.TrimEnd('\') + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Destinazione di build fuori dal progetto.' }
# Evita DLL omonime di altri strumenti (per esempio ICU di Poppler).
# Qt 6.11 usa ICU fornito da Windows, non quello incluso in altri programmi.
try {
    $env:PATH = "$env:SystemRoot\System32;$env:SystemRoot;$(Split-Path -Parent $pythonExe)"
    & $pythonExe -m PyInstaller --clean --noconfirm --onedir --windowed --name AtlanteFormule --icon atlante\assets\atlante.ico --add-data 'atlante/data:atlante/data' --add-data 'atlante/assets:atlante/assets' --add-data 'vendor/node_modules:vendor/node_modules' --collect-data pint --collect-data rapidfuzz --exclude-module scipy --exclude-module tkinter --exclude-module pytest --exclude-module PySide6 --exclude-module PyQt5 --exclude-module IPython main.py
} finally { $env:PATH = $previousPath }
if ($LASTEXITCODE -ne 0) { throw 'Creazione EXE fallita.' }
Copy-Item -LiteralPath 'GUIDA.md','VERIFICHE.md','AUDIT_FORMULE.md','MATERIE.md','requirements-lock.txt','LICENSE','COPYRIGHT.md','THIRD_PARTY.md' -Destination 'dist\AtlanteFormule' -Force
Copy-Item -LiteralPath 'LICENZE' -Destination 'dist\AtlanteFormule\LICENZE' -Recurse -Force
Write-Host 'Pacchetto pronto in dist\AtlanteFormule. Eseguire prima le verifiche del pacchetto, poi tools\package_release.py.'
