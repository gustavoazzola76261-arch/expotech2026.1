# Verifica se o repositorio esta seguro para publicar no GitHub.
# Uso: .\scripts\check-before-github.ps1

$ErrorActionPreference = "Continue"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

$failed = $false

function Fail($msg) {
    Write-Host "[FALHA] $msg" -ForegroundColor Red
    $script:failed = $true
}

function Warn($msg) {
    Write-Host "[AVISO] $msg" -ForegroundColor Yellow
}

function Ok($msg) {
    Write-Host "[OK] $msg" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Campus IoT - verificacao pre-GitHub ===" -ForegroundColor Cyan
Write-Host ""

$mustIgnore = @(
    "backend\.env",
    "frontend\.env",
    "IA\.env",
    "esp32\campus_iot\config.h",
    "crewAI.py"
)

foreach ($rel in $mustIgnore) {
    $path = Join-Path $root $rel
    if (Test-Path $path) {
        Warn "Existe localmente (deve estar no .gitignore): $rel"
    }
}

$git = Get-Command git -ErrorAction SilentlyContinue
if ($null -ne $git) {
    foreach ($rel in $mustIgnore) {
        $norm = $rel -replace "\\", "/"
        $full = Join-Path $root $rel
        if (Test-Path $full) {
            & git check-ignore -q $norm 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Fail "$norm existe mas NAO esta ignorado pelo .gitignore"
            }
        }
        & git ls-files --error-unmatch $norm 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Fail "$norm esta RASTREADO pelo Git - use: git rm --cached $norm"
        }
    }

    $trackedEnv = @(git ls-files 2>$null | Where-Object { $_ -match "\.env$" -and $_ -notmatch "\.example$" })
    if ($trackedEnv.Count -gt 0) {
        Fail ("Arquivos .env rastreados: " + ($trackedEnv -join ", "))
    }

    $allTracked = @(git ls-files 2>$null)
    if ($allTracked -match "^\.venv/|^backend/\.venv/|node_modules") {
        Fail "Ambiente virtual ou node_modules rastreado - remova do Git"
    }
}
else {
    Warn "Git nao encontrado no PATH - pulando checagem de arquivos rastreados"
}

$patterns = @(
    @{ Name = "Groq API key"; Regex = 'gsk_[a-zA-Z0-9]{20,}' },
    @{ Name = "OpenAI-style key"; Regex = 'sk-[a-zA-Z0-9]{20,}' },
    @{ Name = "JWT hardcoded"; Regex = 'eyJ[a-zA-Z0-9_-]{50,}\.[a-zA-Z0-9_-]+\.' }
)

$scanDirs = @("backend\app", "frontend\src", "IA", "esp32", "scripts")
$excludeFiles = @("seed.py", "check-before-github.ps1")

foreach ($dir in $scanDirs) {
    $fullDir = Join-Path $root $dir
    if (-not (Test-Path $fullDir)) { continue }
    $files = Get-ChildItem -Path $fullDir -Recurse -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        if ($file.FullName -match "\\(\.venv|node_modules|__pycache__)\\") { continue }
        if ($excludeFiles -contains $file.Name) { continue }
        if ($file.Name -match "\.example$") { continue }
        $content = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }
        foreach ($p in $patterns) {
            if ($content -match $p.Regex) {
                $relPath = $file.FullName.Substring($root.Length + 1)
                Fail ($p.Name + " possivel em: " + $relPath)
            }
        }
    }
}

Write-Host ""
if ($failed) {
    Write-Host "Corrija os itens acima antes de git push." -ForegroundColor Red
    exit 1
}

Ok "Nenhum problema critico detectado. Revise AVISOs e confira: git status"
exit 0
