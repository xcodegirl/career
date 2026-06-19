param(
    [string]$InputJson,
    [string]$BaseName
)

$ErrorActionPreference = 'Stop'

function Resolve-RepoPath {
    param([string]$PathValue)

    if ([System.IO.Path]::IsPathRooted($PathValue)) {
        return [System.IO.Path]::GetFullPath($PathValue)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot $PathValue))
}

function Resolve-DefaultInputJson {
    $jsonFiles = Get-ChildItem -Path $PSScriptRoot -Filter '*.json' -File
    if ($jsonFiles.Count -eq 1) {
        return $jsonFiles[0].FullName
    }

    if ($jsonFiles.Count -eq 0) {
        throw 'No JSON resume source found in the repo root. Pass -InputJson explicitly.'
    }

    throw 'Multiple JSON files found in the repo root. Pass -InputJson explicitly.'
}

function Get-CommandOrThrow {
    param([string[]]$Names)

    foreach ($name in $Names) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) {
            return $command.Source
        }
    }

    throw "Missing required command: $($Names -join ', ')"
}

$inputPath = if ([string]::IsNullOrWhiteSpace($InputJson)) {
    Resolve-DefaultInputJson
} else {
    Resolve-RepoPath $InputJson
}
if (-not (Test-Path $inputPath)) {
    throw "Input JSON not found: $inputPath"
}

if ([string]::IsNullOrWhiteSpace($BaseName)) {
    $BaseName = [System.IO.Path]::GetFileNameWithoutExtension($inputPath)
}

$outputDir = Split-Path -Parent $inputPath
$latexDir = Join-Path $PSScriptRoot 'latex'
$pythonCmd = Get-CommandOrThrow @('python', 'py')
$pdflatexCmd = Get-Command pdflatex -ErrorAction SilentlyContinue
if (-not $pdflatexCmd) {
    throw 'pdflatex not found on PATH. Install MiKTeX or add its bin folder to PATH first.'
}

$outputs = @{
    Markdown  = Join-Path $outputDir "$BaseName.md"
    Html      = Join-Path $outputDir "$BaseName.html"
    Text      = Join-Path $outputDir "$BaseName.txt"
    Tex       = Join-Path $outputDir "$BaseName.tex"
    Pdf       = Join-Path $outputDir "$BaseName.pdf"
}

Write-Host "Input JSON: $inputPath"
Write-Host "Output directory: $outputDir"

& $pythonCmd (Join-Path $latexDir 'json2md.py') $inputPath $outputs.Markdown
if ($LASTEXITCODE -ne 0) { throw 'Markdown generation failed.' }

& $pythonCmd (Join-Path $latexDir 'json2html.py') $inputPath $outputs.Html
if ($LASTEXITCODE -ne 0) { throw 'HTML generation failed.' }

& $pythonCmd (Join-Path $latexDir 'json2txt.py') $inputPath $outputs.Text
if ($LASTEXITCODE -ne 0) { throw 'Plain-text generation failed.' }

& $pythonCmd (Join-Path $latexDir 'json2tex.py') $inputPath $outputs.Tex
if ($LASTEXITCODE -ne 0) { throw 'LaTeX generation failed.' }

Push-Location $outputDir
try {
    $originalTexInputs = $env:TEXINPUTS
    $env:TEXINPUTS = "$latexDir;"
    & $pdflatexCmd.Source -interaction=nonstopmode -jobname $BaseName -output-directory $outputDir (Split-Path -Leaf $outputs.Tex)
    if ($LASTEXITCODE -ne 0) { throw 'PDF build failed.' }
}
finally {
    $env:TEXINPUTS = $originalTexInputs
    Pop-Location
}

foreach ($suffix in @('aux', 'log', 'out')) {
    $artifactPath = Join-Path $outputDir "$BaseName.$suffix"
    if (Test-Path $artifactPath) {
        Remove-Item $artifactPath -Force
    }
}

Write-Host "Wrote Markdown: $($outputs.Markdown)"
Write-Host "Wrote HTML: $($outputs.Html)"
Write-Host "Wrote plain text: $($outputs.Text)"
Write-Host "Wrote LaTeX: $($outputs.Tex)"
Write-Host "Wrote PDF: $($outputs.Pdf)"
