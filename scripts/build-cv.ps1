#
# Build all resume formats from JSON source.
# Runs json2* converters to generate Markdown, HTML, plain text, PDF, and Word formats.
#

param(
    [string]$InputJson,
    [string]$BaseName,
    [string]$OutputDir
)

$ErrorActionPreference = 'Stop'

#=========================================================================
# UTILITY FUNCTIONS
#=========================================================================

function Resolve-FilePath {
    # Convert path to absolute, resolving relative paths from caller cwd.
    param([string]$path)

    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($path)
}


function Find-Command {
    # Locate command on PATH, error if not found.
    param([string[]]$names)

    foreach ($name in $names) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) {
            return $cmd.Source
        }
    }

    throw "Missing required command: $($names -join ', ')"
}


function Test-FileLocked {
    # Returns $true if the file exists and cannot be opened exclusively.
    param([string]$path)
    if (-not (Test-Path $path)) { return $false }
    try {
        $stream = [System.IO.File]::Open(
            $path,
            [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::ReadWrite,
            [System.IO.FileShare]::None
        )
        $stream.Close()
        return $false
    } catch {
        return $true
    }
}


function Wait-FileUnlocked {
    # Loops until the file is free or the user skips. Returns $true to proceed, $false to skip.
    param([string]$path, [string]$label)
    while (Test-FileLocked $path) {
        Write-Host ""
        Write-Host "  $label is open in another application." -ForegroundColor Yellow
        Write-Host "  Close it, then press Enter to retry -- or type S and Enter to skip." -ForegroundColor Yellow
        $response = Read-Host "  [Enter / S]"
        if ($response -match '^[Ss]$') { return $false }
    }
    return $true
}


function Get-PythonExecutable {
    # Find Python interpreter: check virtual env, repo venv, then PATH.
    param([string]$repoRoot)

    # Check active virtual environment.
    if (-not [string]::IsNullOrWhiteSpace($env:VIRTUAL_ENV)) {
        $activePython = Join-Path $env:VIRTUAL_ENV 'Scripts\python.exe'
        if (Test-Path $activePython) {
            return $activePython
        }
    }

    # Check repo .venv.
    $repoPython = Join-Path $repoRoot '.venv\Scripts\python.exe'
    if (Test-Path $repoPython) {
        return $repoPython
    }

    # Fall back to PATH.
    return Find-Command @('python', 'py')
}

#=========================================================================
# RESOLVE PATHS AND VERIFY TOOLS
#=========================================================================

# Resolve input and output paths.
if ([string]::IsNullOrWhiteSpace($InputJson)) {
    throw 'InputJson is required. Usage: .\build-cv.ps1 -InputJson path\to\resume.json -OutputDir path [-BaseName name]'
}

$inputPath = Resolve-FilePath $InputJson

if (-not (Test-Path $inputPath)) {
    throw "Input JSON not found: $inputPath"
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$scriptsDir = $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    throw 'OutputDir is required. Usage: .\build-cv.ps1 -InputJson path\to\resume.json -OutputDir path [-BaseName name]'
}

if ([string]::IsNullOrWhiteSpace($BaseName)) {
    $BaseName = [System.IO.Path]::GetFileNameWithoutExtension($inputPath)
}

$outputDir = Resolve-FilePath $OutputDir

# Ensure output directory exists.
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# Verify tools are available.
$pythonCmd = Get-PythonExecutable $repoRoot
Get-Command pdflatex -ErrorAction SilentlyContinue | Out-Null
if (-not $?) {
    throw 'pdflatex not found on PATH. Install MiKTeX or add its bin folder to PATH first.'
}

#=========================================================================
# DEFINE OUTPUT PATHS AND BUILD ALL FORMATS
#=========================================================================

# Define output file paths.
$outputs = @{
    Markdown  = Join-Path $outputDir "$BaseName.md"
    Html      = Join-Path $outputDir "$BaseName.html"
    Text      = Join-Path $outputDir "$BaseName.txt"
    Pdf       = Join-Path $outputDir "$BaseName.pdf"
    Docx      = Join-Path $outputDir "$BaseName.docx"
}

Write-Host "Input JSON: $inputPath"
Write-Host "Output directory: $outputDir"
Write-Host ""

# Generate all formats.
Write-Host "Generating Markdown..." -ForegroundColor Cyan
& $pythonCmd (Join-Path $scriptsDir 'json2md.py') $inputPath $outputs.Markdown
if ($LASTEXITCODE -ne 0) { throw 'Markdown generation failed.' }

Write-Host "Generating HTML..." -ForegroundColor Cyan
& $pythonCmd (Join-Path $scriptsDir 'json2html.py') $inputPath $outputs.Html
if ($LASTEXITCODE -ne 0) { throw 'HTML generation failed.' }

Write-Host "Generating plain text..." -ForegroundColor Cyan
& $pythonCmd (Join-Path $scriptsDir 'json2txt.py') $inputPath $outputs.Text
if ($LASTEXITCODE -ne 0) { throw 'Plain-text generation failed.' }

Write-Host "Generating PDF (article style)..." -ForegroundColor Cyan
if (Wait-FileUnlocked $outputs.Pdf "PDF ($($outputs.Pdf))") {
    & $pythonCmd (Join-Path $scriptsDir 'json2pdf.py') $inputPath $outputs.Pdf
    if ($LASTEXITCODE -ne 0) { throw 'PDF generation failed (article style).' }
} else {
    Write-Host "  Skipped PDF generation." -ForegroundColor Yellow
}

Write-Host "Generating Word document..." -ForegroundColor Cyan
& $pythonCmd (Join-Path $scriptsDir 'json2docx.py') $inputPath $outputs.Docx
if ($LASTEXITCODE -ne 0) { throw 'Word document generation failed.' }

Write-Host ""
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "Output files:"
Write-Host "  Markdown: $($outputs.Markdown)"
Write-Host "  HTML: $($outputs.Html)"
Write-Host "  Plain text: $($outputs.Text)"
Write-Host "  PDF: $($outputs.Pdf)"
Write-Host "  Word: $($outputs.Docx)"
