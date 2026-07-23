param(
    [string]$Output = "",
    [switch]$DryRun,
    [switch]$NoPause
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Pause-IfNeeded {
    if (-not $NoPause) {
        [void](Read-Host "按 Enter 键关闭窗口")
    }
}

function Stop-WithMessage([string]$Message, [int]$Code = 1) {
    Write-Host "[失败] $Message" -ForegroundColor Red
    Pause-IfNeeded
    exit $Code
}

function Find-PythonExecutable {
    $venvPython = Join-Path $Root ".venv-windows\Scripts\python.exe"
    if (Test-Path $venvPython) {
        return $venvPython
    }

    $python = Get-Command "python.exe" -ErrorAction SilentlyContinue
    if ($python) {
        return $python.Source
    }

    $py = Get-Command "py.exe" -ErrorAction SilentlyContinue
    if ($py) {
        return $py.Source
    }
    return $null
}

Write-Host "============================================================" -ForegroundColor DarkCyan
Write-Host " 开源硬件商业化机会库 - Windows 结果验收" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor DarkCyan

$validator = Join-Path $Root "scripts\validate_output.py"
if (-not (Test-Path $validator)) {
    Stop-WithMessage "缺少 scripts\validate_output.py，请完整解压仓库。"
}

$python = Find-PythonExecutable
if (-not $python) {
    Stop-WithMessage "未找到 Python。请先双击 RUN_WINDOWS.bat 完成环境初始化。"
}

if ($DryRun) {
    Write-Host "DryRun 通过：验收脚本和 Python 已找到。" -ForegroundColor Green
    Pause-IfNeeded
    exit 0
}

if ([string]::IsNullOrWhiteSpace($Output)) {
    $inputPath = Read-Host "结果目录 [默认 output_v2]"
    $Output = if ([string]::IsNullOrWhiteSpace($inputPath)) { "output_v2" } else { $inputPath.Trim().Trim('"') }
}
$outputFullPath = if ([System.IO.Path]::IsPathRooted($Output)) { $Output } else { Join-Path $Root $Output }

if (-not (Test-Path $outputFullPath)) {
    Stop-WithMessage "结果目录不存在：$outputFullPath"
}

if ([System.IO.Path]::GetFileName($python).ToLowerInvariant() -eq "py.exe") {
    & $python -3 $validator $outputFullPath
}
else {
    & $python $validator $outputFullPath
}
$validationExitCode = $LASTEXITCODE

if ($validationExitCode -ne 0) {
    Stop-WithMessage "验收未通过，退出码 $validationExitCode。请根据上方提示检查文件。" $validationExitCode
}

Write-Host ""
Write-Host "验收通过。" -ForegroundColor Green
$xlsxPath = Join-Path $outputFullPath "开源硬件商业化机会库_10000条.xlsx"
if (Test-Path $xlsxPath) {
    Write-Host "Excel：$xlsxPath"
    $openAnswer = Read-Host "是否现在打开 Excel？[Y/n]"
    if (-not $openAnswer -or $openAnswer.Trim().ToLowerInvariant() -in @("y", "yes", "是")) {
        Start-Process $xlsxPath
    }
}

Pause-IfNeeded
exit 0
