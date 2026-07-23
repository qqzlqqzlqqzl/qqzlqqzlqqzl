param(
    [int]$Target = 0,
    [string]$Output = "",
    [string]$GitHubToken = "",
    [switch]$DryRun,
    [switch]$NoPause,
    [switch]$SkipValidation
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
    Write-Host ""
    Write-Host "[失败] $Message" -ForegroundColor Red
    Pause-IfNeeded
    exit $Code
}

function Test-PythonCommand([string]$File, [string[]]$Prefix) {
    try {
        $arguments = @($Prefix) + @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)")
        & $File @arguments *> $null
        return ($LASTEXITCODE -eq 0)
    }
    catch {
        return $false
    }
}

function Find-Python {
    $py = Get-Command "py.exe" -ErrorAction SilentlyContinue
    if ($py) {
        if (Test-PythonCommand $py.Source @("-3.12")) {
            return @{ File = $py.Source; Prefix = @("-3.12"); Label = "Python 3.12 (py launcher)" }
        }
        if (Test-PythonCommand $py.Source @("-3")) {
            return @{ File = $py.Source; Prefix = @("-3"); Label = "Python 3 (py launcher)" }
        }
    }

    $python = Get-Command "python.exe" -ErrorAction SilentlyContinue
    if ($python -and (Test-PythonCommand $python.Source @())) {
        return @{ File = $python.Source; Prefix = @(); Label = "Python" }
    }

    $knownPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python311\python.exe"
    )
    foreach ($candidate in $knownPaths) {
        if ((Test-Path $candidate) -and (Test-PythonCommand $candidate @())) {
            return @{ File = $candidate; Prefix = @(); Label = $candidate }
        }
    }
    return $null
}

function Install-PythonIfApproved {
    $winget = Get-Command "winget.exe" -ErrorAction SilentlyContinue
    if (-not $winget) {
        return $false
    }

    $answer = Read-Host "没有检测到 Python 3.10+。是否使用 winget 自动安装 Python 3.12？[Y/n]"
    if ($answer -and $answer.Trim().ToLowerInvariant() -notin @("y", "yes", "是")) {
        return $false
    }

    Write-Host "正在通过 winget 安装 Python 3.12（当前用户）……" -ForegroundColor Cyan
    & $winget.Source install --exact --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        return $false
    }
    return $true
}

Write-Host "============================================================" -ForegroundColor DarkCyan
Write-Host " 开源硬件商业化机会库 - Windows 一键运行" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor DarkCyan
Write-Host "仓库目录：$Root"

$requiredFiles = @(
    "crawler\v2.py",
    "crawler\requirements.txt",
    "scripts\validate_output.py"
)
foreach ($relativePath in $requiredFiles) {
    if (-not (Test-Path (Join-Path $Root $relativePath))) {
        Stop-WithMessage "缺少文件：$relativePath。请完整解压仓库后再运行。"
    }
}

$pythonLauncher = Find-Python
if (-not $pythonLauncher -and -not $DryRun) {
    if (Install-PythonIfApproved) {
        $pythonLauncher = Find-Python
    }
}
if (-not $pythonLauncher) {
    if ($DryRun) {
        Stop-WithMessage "DryRun 未找到 Python 3.10+。" 2
    }
    Start-Process "https://www.python.org/downloads/windows/"
    Stop-WithMessage "未找到 Python 3.10+，自动安装也未成功。已打开 Python 下载页面；安装时请勾选 Add python.exe to PATH。"
}
Write-Host "Python：$($pythonLauncher.Label)" -ForegroundColor Green

if ($DryRun) {
    Write-Host "DryRun 通过：入口文件、Python 和目录结构正常。" -ForegroundColor Green
    Pause-IfNeeded
    exit 0
}

if ($Target -le 0) {
    $targetInput = Read-Host "最终目标条数 [默认 10500]"
    if ([string]::IsNullOrWhiteSpace($targetInput)) {
        $Target = 10500
    }
    elseif (-not [int]::TryParse($targetInput, [ref]$Target) -or $Target -le 0) {
        Stop-WithMessage "目标条数必须是正整数。"
    }
}

if ([string]::IsNullOrWhiteSpace($Output)) {
    $outputInput = Read-Host "输出目录 [默认 output_v2]"
    $Output = if ([string]::IsNullOrWhiteSpace($outputInput)) { "output_v2" } else { $outputInput.Trim() }
}

if ($Target -lt 10000) {
    Write-Host "提示：目标少于 10000 时，程序会生成文件，但正式质量门槛会返回非零退出码。这适合测试，不算正式交付。" -ForegroundColor Yellow
}

if (-not [string]::IsNullOrWhiteSpace($GitHubToken)) {
    $env:GITHUB_TOKEN = $GitHubToken
}
elseif (-not $env:GITHUB_TOKEN) {
    Write-Host ""
    Write-Host "建议提供 GitHub Token，可显著降低 GitHub API 限流。Token 只保存在本次进程内，不会写入磁盘。" -ForegroundColor Yellow
    $secureToken = Read-Host "粘贴 Token（不需要可直接按 Enter）" -AsSecureString
    $tokenPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
    try {
        $plainToken = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($tokenPointer)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($tokenPointer)
    }
    if (-not [string]::IsNullOrWhiteSpace($plainToken)) {
        $env:GITHUB_TOKEN = $plainToken
    }
}

$venvPath = Join-Path $Root ".venv-windows"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host ""
    Write-Host "首次运行：正在创建独立 Python 环境……" -ForegroundColor Cyan
    $venvArguments = @($pythonLauncher.Prefix) + @("-m", "venv", $venvPath)
    & $pythonLauncher.File @venvArguments
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $venvPython)) {
        Stop-WithMessage "创建虚拟环境失败。"
    }
}

$requirements = Join-Path $Root "crawler\requirements.txt"
$requirementsHash = (Get-FileHash $requirements -Algorithm SHA256).Hash
$markerFile = Join-Path $venvPath ".requirements.sha256"
$installedHash = if (Test-Path $markerFile) { (Get-Content $markerFile -Raw).Trim() } else { "" }
if ($installedHash -ne $requirementsHash) {
    Write-Host ""
    Write-Host "正在安装或更新依赖……" -ForegroundColor Cyan
    & $venvPython -m pip install --disable-pip-version-check --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        Stop-WithMessage "升级 pip 失败。"
    }
    & $venvPython -m pip install --disable-pip-version-check -r $requirements
    if ($LASTEXITCODE -ne 0) {
        Stop-WithMessage "安装依赖失败，请检查网络、代理或安全软件。"
    }
    Set-Content -Path $markerFile -Value $requirementsHash -Encoding ASCII
}
else {
    Write-Host "依赖已经安装，无需重复下载。" -ForegroundColor DarkGreen
}

$outputFullPath = if ([System.IO.Path]::IsPathRooted($Output)) { $Output } else { Join-Path $Root $Output }
Write-Host ""
Write-Host "开始抓取：目标 $Target 条" -ForegroundColor Cyan
Write-Host "输出目录：$outputFullPath"
Write-Host "运行期间请不要关闭此窗口。部分网站响应慢属于正常情况。" -ForegroundColor Yellow
Write-Host ""

$runArguments = @("crawler\v2.py", "--target", $Target.ToString(), "--out", $outputFullPath)
& $venvPython @runArguments
$crawlExitCode = $LASTEXITCODE

$csvPath = Join-Path $outputFullPath "hardware_opportunities.csv"
if ($crawlExitCode -ne 0) {
    if ((Test-Path $csvPath) -and $Target -lt 10000) {
        Write-Host "测试数据已生成；退出码 $crawlExitCode 来自正式 10k 质量门槛。" -ForegroundColor Yellow
    }
    else {
        Stop-WithMessage "抓取程序退出码为 $crawlExitCode。请查看窗口上方的错误信息和输出目录中的 progress/source_status 文件。" $crawlExitCode
    }
}

if (-not $SkipValidation -and $Target -ge 10000) {
    Write-Host ""
    Write-Host "正在自动验收结果……" -ForegroundColor Cyan
    & $venvPython "scripts\validate_output.py" $outputFullPath
    if ($LASTEXITCODE -ne 0) {
        Stop-WithMessage "数据已生成，但自动验收未通过。请查看上方具体项目。" 3
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor DarkGreen
Write-Host " 完成" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor DarkGreen
Write-Host "结果目录：$outputFullPath"
$xlsxPath = Join-Path $outputFullPath "开源硬件商业化机会库_10000条.xlsx"
if (Test-Path $xlsxPath) {
    Write-Host "优先打开：$xlsxPath"
}

try {
    Start-Process explorer.exe -ArgumentList ('"' + $outputFullPath + '"')
}
catch {
    Write-Host "无法自动打开资源管理器，请手动打开结果目录。" -ForegroundColor Yellow
}

Pause-IfNeeded
exit 0
