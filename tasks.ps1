<#
.SYNOPSIS
    Trinh chay tac vu cho kho DRA AI Tutor Research (ban PowerShell cua Makefile).

.EXAMPLE
    ./tasks.ps1 check
    ./tasks.ps1 all
#>

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('help', 'validate', 'stats', 'splits', 'export', 'figures', 'test', 'lint', 'coverage', 'baseline', 'report', 'all', 'check', 'clean')]
    [string]$Task = 'help'
)

$ErrorActionPreference = 'Stop'
$python = 'python'

function Invoke-Step {
    param([string]$Description, [string[]]$Arguments)

    Write-Host "==> $Description" -ForegroundColor Cyan
    & $python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "That bai: $Description (ma thoat $LASTEXITCODE)"
    }
}

switch ($Task) {
    'help' {
        Write-Host 'Cac tac vu:'
        Write-Host '  validate  Kiem dinh schema va quy uoc du lieu'
        Write-Host '  splits    Sinh lai datasets/splits/'
        Write-Host '  stats     Sinh lai docs/dataset_stats.md'
        Write-Host '  export    Sinh lai datasets/exports/'
        Write-Host '  figures   Sinh lai figures/*.svg'
        Write-Host '  test      Chay toan bo test'
        Write-Host '  baseline  Chay danh gia baseline dinh tuyen'
        Write-Host '  report    Sinh lai ket qua baseline (markdown + JSON)'
        Write-Host '  lint      Chay ruff (can requirements-dev.txt)'
        Write-Host '  coverage  Chay test kem do coverage (can requirements-dev.txt)'
        Write-Host '  all       Sinh lai moi thu roi chay test'
        Write-Host '  check     Kiem tra file sinh tu dong da cap nhat (dung cho CI)'
        Write-Host '  clean     Xoa cache Python'
    }
    'validate' { Invoke-Step 'Kiem dinh du lieu' @('tools/validate_datasets.py', '--strict') }
    'stats'    { Invoke-Step 'Sinh thong ke'     @('tools/dataset_stats.py') }
    'splits'   { Invoke-Step 'Sinh split'        @('tools/make_splits.py') }
    'export'   { Invoke-Step 'Xuat du lieu gop'  @('tools/export_dataset.py') }
    'figures'  { Invoke-Step 'Sinh hinh ve'      @('tools/make_figures.py') }
    'test'     { Invoke-Step 'Chay test'         @('-m', 'unittest', 'discover', '-s', 'tests', '-v') }
    'baseline' { Invoke-Step 'Baseline dinh tuyen' @('tools/baseline_router.py') }
    'report'   { Invoke-Step 'Sinh bao cao baseline' @('tools/baseline_router.py', '--report') }
    'lint'     { Invoke-Step 'Lint bang ruff'    @('-m', 'ruff', 'check', 'tools', 'tests') }
    'coverage' {
        Invoke-Step 'Chay test kem coverage' @('-m', 'coverage', 'run', '-m', 'unittest', 'discover', '-s', 'tests')
        Invoke-Step 'Bao cao coverage'       @('-m', 'coverage', 'report')
    }
    'all' {
        Invoke-Step 'Kiem dinh du lieu'    @('tools/validate_datasets.py', '--strict')
        Invoke-Step 'Sinh split'           @('tools/make_splits.py')
        Invoke-Step 'Sinh thong ke'        @('tools/dataset_stats.py')
        Invoke-Step 'Xuat du lieu gop'     @('tools/export_dataset.py')
        Invoke-Step 'Sinh ket qua baseline' @('tools/baseline_router.py', '--report')
        Invoke-Step 'Sinh hinh ve'         @('tools/make_figures.py')
        Invoke-Step 'Chay test'            @('-m', 'unittest', 'discover', '-s', 'tests', '-v')
    }
    'check' {
        Invoke-Step 'Kiem dinh du lieu'    @('tools/validate_datasets.py', '--strict')
        Invoke-Step 'Kiem tra split'       @('tools/make_splits.py', '--check')
        Invoke-Step 'Kiem tra thong ke'    @('tools/dataset_stats.py', '--check')
        Invoke-Step 'Kiem tra file xuat'   @('tools/export_dataset.py', '--check')
        Invoke-Step 'Kiem tra ket qua'     @('tools/baseline_router.py', '--check')
        Invoke-Step 'Kiem tra hinh ve'     @('tools/make_figures.py', '--check')
        Invoke-Step 'Chay test'            @('-m', 'unittest', 'discover', '-s', 'tests')
    }
    'clean' {
        foreach ($path in @('tools/__pycache__', 'tests/__pycache__')) {
            if (Test-Path $path) { Remove-Item -Recurse -Force $path }
        }
        Write-Host 'Da xoa cache Python.'
    }
}
