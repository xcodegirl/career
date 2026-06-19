#
# Build all resume formats from JSON source.
# Runs json2* converters to generate Markdown, HTML, plain text, PDF, and Word formats.
#

param(
    [string]$InputJson,
    [string]$BaseName
)

$ErrorActionPreference = 'Stop'

#=========================================================================
# UTILITY FUNCTIONS
#=========================================================================

function Resolve-FilePath {
    # Convert path to absolute, handling both relative and rooted paths.
    param([string]$path)

    if ([System.IO.Path]::IsPathRooted($path)) {
        return [System.IO.Path]::GetFullPath($path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot $path))
}


function Find-ResumeJsonSource {
    # Locate JSON resume file: error if missing or multiple candidates.
    $jsonFiles = Get-ChildItem -Path $PSScriptRoot -Filter '*.json' -File | Where-Object { $_.Name -notlike 'testuser*' }

    if ($jsonFiles.Count -eq 1) {
        return $jsonFiles[0].FullName
    }

    if ($jsonFiles.Count -eq 0) {
        throw 'No JSON resume source found in scripts/. Pass -InputJson explicitly.'
    }

    throw 'Multiple JSON files found in scripts/. Pass -InputJson explicitly.'
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
$inputPath = if ([string]::IsNullOrWhiteSpace($InputJson)) {
    Find-ResumeJsonSource
} else {
    Resolve-FilePath $InputJson
}

if (-not (Test-Path $inputPath)) {
    throw "Input JSON not found: $inputPath"
}

if ([string]::IsNullOrWhiteSpace($BaseName)) {
    $BaseName = [System.IO.Path]::GetFileNameWithoutExtension($inputPath)
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$outputDir = Join-Path $repoRoot 'formatted'
$scriptsDir = $PSScriptRoot

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
& $pythonCmd (Join-Path $scriptsDir 'json2pdf.py') $inputPath $outputs.Pdf
if ($LASTEXITCODE -ne 0) { throw 'PDF generation failed (article style).' }

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
