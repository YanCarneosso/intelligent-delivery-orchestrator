param(
    [ValidateSet('setup', 'test', 'demo', 'lint', 'format-check', 'typecheck', 'validate', 'security', 'ci', 'benchmark')]
    [string]$Command = 'ci'
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'

if ($Command -eq 'setup') {
    python -m venv (Join-Path $ProjectRoot '.venv')
    & $Python -m pip install --upgrade pip
    & $Python -m pip install -e "${ProjectRoot}[dev,aws]"
    exit $LASTEXITCODE
}

if (-not (Test-Path -LiteralPath $Python)) {
    throw 'Run .\scripts\dev.ps1 setup first.'
}

$Commands = @{
    'test' = @('-m', 'pytest', '-m', 'not integration')
    'demo' = @('-m', 'delivery_orchestrator.cli')
    'lint' = @('-m', 'ruff', 'check', '.')
    'format-check' = @('-m', 'ruff', 'format', '--check', '.')
    'typecheck' = @('-m', 'mypy')
    'validate' = @('scripts/validate_repository.py')
    'security' = @('scripts/secret_scan.py')
    'benchmark' = @('scripts/benchmark.py', '--iterations', '500')
}

Push-Location $ProjectRoot
try {
    if ($Command -eq 'ci') {
        foreach ($Step in @('lint', 'format-check', 'typecheck', 'validate', 'security', 'test')) {
            & $Python @($Commands[$Step])
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        }
    } else {
        & $Python @($Commands[$Command])
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}
