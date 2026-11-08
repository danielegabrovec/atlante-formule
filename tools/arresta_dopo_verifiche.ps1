param([switch]$Arm, [ValidateRange(5,120)][int]$DelaySeconds = 20)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$evidenceRoot = Join-Path $projectRoot 'verifiche'
$distributionRoot = Join-Path $projectRoot 'dist'

# Nessun arresto se manca una sola prova della consegna finale.
[xml]$testReport = Get-Content -Raw -LiteralPath (Join-Path $evidenceRoot 'test-results.xml')
$suites = @($testReport.SelectNodes('//testsuite'))
if ($suites.Count -eq 0) { throw 'Rapporto test mancante o vuoto.' }
foreach ($suite in $suites) {
    if ([int]$suite.tests -le 0 -or [int]$suite.failures -ne 0 -or [int]$suite.errors -ne 0) { throw 'Test non superati.' }
}
foreach ($reportName in @('package-smoke.json','package-smoke-dpi150.json')) {
    $packageReport = Get-Content -Raw -LiteralPath (Join-Path $evidenceRoot $reportName) | ConvertFrom-Json
    if ($packageReport.ok -ne $true -or $packageReport.frozen -ne $true -or $packageReport.catalog_size -ne 988 -or $packageReport.sections -ne $true -or $packageReport.icons -ne $true) { throw "Pacchetto non verificato: $reportName" }
}
$audit = Get-Content -Raw -LiteralPath (Join-Path $evidenceRoot 'audit-formule.json') | ConvertFrom-Json
if ($audit.cards -ne 988 -or @($audit.errors).Count -ne 0) { throw 'Audit non superato.' }
foreach ($line in (Get-Content -LiteralPath (Join-Path $distributionRoot 'SHA256SUMS.txt'))) {
    if ($line -notmatch '^([0-9a-fA-F]{64})\s+([^\\/]+\.zip)$') { throw 'Manifest non valido.' }
    $expectedHash = $Matches[1]; $zipName = $Matches[2]
    $actualHash = (Get-FileHash -LiteralPath (Join-Path $distributionRoot $zipName) -Algorithm SHA256).Hash
    if (-not $actualHash.Equals($expectedHash,[StringComparison]::OrdinalIgnoreCase)) { throw "Hash non valido: $zipName" }
}
if (-not $Arm) {
    Write-Output 'Tutte le verifiche sono superate. Modalità di controllo: arresto non avviato.'
    exit 0
}

$statusFile = Join-Path $evidenceRoot 'arresto-sistema.json'
@{status='programmato';utc=[DateTime]::UtcNow.ToString('o');delay_seconds=$DelaySeconds;reason='Richiesta esplicita utente dopo correzione, test e consegna verificata'} | ConvertTo-Json | Set-Content -LiteralPath $statusFile -Encoding UTF8
Start-Sleep -Seconds $DelaySeconds
@{status='richiesta_di_arresto';utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath $statusFile -Encoding UTF8
# Timeout zero evita la chiusura forzata implicita nei timeout nativi >0.
& "$env:SystemRoot\System32\shutdown.exe" /s /t 0 /d p:0:0 /c 'Atlante Formule: lavoro completato e verificato, arresto richiesto.'
if ($LASTEXITCODE -ne 0) {
    @{status='arresto_non_riuscito';utc=[DateTime]::UtcNow.ToString('o');exit_code=$LASTEXITCODE} | ConvertTo-Json | Set-Content -LiteralPath $statusFile -Encoding UTF8
    exit $LASTEXITCODE
}
