# CV Generation Guide

Generate CVs from a single JSON source into PDF, LaTeX, Markdown, HTML, DOCX, and plain text.

You can run the scripts from outside the `scripts/` folder, use a JSON file anywhere on disk, and send the generated outputs to any directory you choose.

This document reflects the scripts currently present in this repo. It was validated against a synthetic test resume, `jimbo-resume.json`, on 2026-06-21.

## What Exists in This Repo

Supported scripts in `scripts/`:

- `build-cv.ps1` and `build-cv.bat`
- `json2pdf.py`
- `json2tex.py`
- `json2md.py`
- `json2html.py`
- `json2docx.py`
- `json2txt.py`

There is currently one supported PDF style: the article-style pipeline driven by `json2tex.py` and `json2pdf.py`.

## Quick Start

### From the repo root

```powershell
# PowerShell entrypoint requires explicit input and output paths
.\scripts\build-cv.ps1 -InputJson .\scripts\jhoar-resume.json -OutputDir .\formatted

# Build from a specific JSON file in scripts/
.\scripts\build-cv.ps1 -InputJson jhoar-resume.json -OutputDir .\formatted

# Build from the synthetic process-test resume
.\scripts\build-cv.ps1 -InputJson jimbo-resume.json -OutputDir .\formatted -BaseName jimbo-resume

# Build from any JSON path and write outputs to any directory
.\scripts\build-cv.ps1 -InputJson .\scripts\jimbo-resume.json -OutputDir .\tmp\cv-out -BaseName external-run
```

### From the `scripts/` directory

```powershell
.\build-cv.ps1 -InputJson .\jhoar-resume.json -OutputDir ..\formatted
.\build-cv.ps1 -InputJson jhoar-resume.json -OutputDir ..\formatted
.\build-cv.ps1 -InputJson jimbo-resume.json -OutputDir ..\formatted -BaseName jimbo-resume
.\build-cv.ps1 -InputJson C:\Resumes\candidate.json -OutputDir C:\Resumes\build -BaseName candidate
```

With no `-InputJson`, `build-cv.ps1` now stops with an explicit `InputJson is required` error.
With no `-OutputDir`, `build-cv.ps1` now stops with an explicit `OutputDir is required` error.

### Batch File Default

`build-cv.bat` is the convenience wrapper for the repository's default resume.

When you run it with no arguments, it builds `jhoar-resume.json` and writes outputs to `formatted/`.

If you pass arguments to the batch file, they are forwarded to `build-cv.ps1`.

### Path Behavior

`build-cv.ps1` now resolves relative `-InputJson` and `-OutputDir` paths from your current working directory, so you can call it naturally from outside `scripts/`.

Examples from the repo root:

```powershell
.\scripts\build-cv.ps1 -InputJson .\scripts\jimbo-resume.json -OutputDir .\tmp\cv-out
```

Examples with absolute paths anywhere on disk:

```powershell
.\scripts\build-cv.ps1 -InputJson C:\Users\you\Documents\resume.json -OutputDir D:\CVs\exports -BaseName tailored-resume
```

`build-cv.ps1` does not have a default output directory. Pass `-OutputDir` explicitly.

## Direct Python Calls

These commands work from any current directory as long as you point at the script file correctly.

```bash
# PDF (also writes an intermediate .tex file)
python c:\Users\linux\source\repos\career\scripts\json2pdf.py c:\path\to\resume.json c:\path\to\output\resume.pdf

# LaTeX only
python c:\Users\linux\source\repos\career\scripts\json2tex.py c:\path\to\resume.json c:\path\to\output\resume.tex

# Markdown
python c:\Users\linux\source\repos\career\scripts\json2md.py c:\path\to\resume.json c:\path\to\output\resume.md

# HTML
python c:\Users\linux\source\repos\career\scripts\json2html.py c:\path\to\resume.json c:\path\to\output\resume.html

# DOCX
python c:\Users\linux\source\repos\career\scripts\json2docx.py c:\path\to\resume.json c:\path\to\output\resume.docx

# Plain text
python c:\Users\linux\source\repos\career\scripts\json2txt.py c:\path\to\resume.json c:\path\to\output\resume.txt
```

## Build Pipeline

`build-cv.ps1` generates:

- Markdown
- HTML
- plain text
- PDF
- DOCX

The PDF step also creates an intermediate `.tex` file beside the PDF output.

Parameters:

- `-InputJson` required path to a JSON file anywhere on disk
- `-OutputDir` required directory for all generated outputs
- `-BaseName` optional filename stem for all generated outputs

Typical output files for `-OutputDir formatted -BaseName jimbo-resume`:

- `formatted/jimbo-resume.md`
- `formatted/jimbo-resume.html`
- `formatted/jimbo-resume.txt`
- `formatted/jimbo-resume.pdf`
- `formatted/jimbo-resume.docx`
- `formatted/jimbo-resume.tex`

Typical output files for `-OutputDir C:\CVs\build -BaseName tailored-resume`:

- `C:\CVs\build\tailored-resume.md`
- `C:\CVs\build\tailored-resume.html`
- `C:\CVs\build\tailored-resume.txt`
- `C:\CVs\build\tailored-resume.pdf`
- `C:\CVs\build\tailored-resume.docx`
- `C:\CVs\build\tailored-resume.tex`

## JSON Schema in Practice

There is no separate schema file in this repo right now. Use these files as the contract:

- `jhoar-resume.json` for a real example
- `jimbo-resume.json` for a synthetic process-test example that exercises more optional sections

Common top-level fields:

- `name`
- `title`
- `contact`
- `summary`
- `ai_expertise`
- `experience`
- `education`
- `certifications`
- `awards`
- `skills`
- `projects`
- `volunteer`
- `publications`
- `languages`
- `memberships`
- `portfolio`
- `published_games`
- `section_order`
- `section_filter`

### Recommended Shape for Reliable Cross-Format Output

For the smoothest results across all current converters:

- Prefer `experience` over `teaching_experience` or `industry_experience`
- Prefer `bullets` arrays for experience entries
- Treat `description` on experience entries as legacy compatibility, not the main path
- Keep optional fields genuinely optional; missing sections are skipped cleanly

## Section Ordering and Filtering

All current generators respect `section_order` and `section_filter`.

### `section_order`

Provide an array of section names in the order you want rendered.
Only the listed sections are considered.

```json
{
  "name": "Jane Doe",
  "section_order": ["summary", "skills", "experience", "education"]
}
```

### `section_filter`

Provide an array of section names to suppress.

```json
{
  "name": "Jane Doe",
  "section_filter": ["published_games", "volunteer"]
}
```

You can combine both fields. The synthetic `jimbo-resume.json` does this to prove the behavior end to end.

Default section order when `section_order` is omitted:

1. Summary
2. AI Expertise
3. Experience
4. Education
5. Certifications
6. Awards
7. Skills
8. Projects
9. Volunteer
10. Publications
11. Languages
12. Memberships
13. Portfolio
14. Published Games

## LaTeX and PDF Notes

`json2tex.py` generates article-style LaTeX using:

- `article`
- `geometry`
- `titlesec`
- `hyperref`
- `fontawesome5`
- `raleway`

`json2pdf.py` calls `json2tex.py`, then runs `pdflatex` and removes `.aux`, `.log`, and `.out` artifacts after a successful compile.

If you want to customize the PDF styling, edit the generated `.tex` file or the Python generator.

## Requirements

- Python 3.7+
- `pdflatex` on `PATH`
- `python-docx` installed in the interpreter used by the build script

Verify setup:

```powershell
python --version
pdflatex --version
pip show python-docx
```

The build script prefers:

1. the active virtual environment
2. `repo/.venv/Scripts/python.exe`
3. `python` or `py` on `PATH`

## Directory Structure

```text
career/
|-- formatted/
|-- scripts/
|   |-- build-cv.bat
|   |-- build-cv.ps1
|   |-- CV-GENERATION.md
|   |-- jhoar-resume.json
|   |-- jimbo-resume.json
|   |-- json2docx.py
|   |-- json2html.py
|   |-- json2md.py
|   |-- json2pdf.py
|   |-- json2tex.py
|   `-- json2txt.py
`-- .venv/
```

## Troubleshooting

### `pdflatex not found`

Install MiKTeX or TeX Live and ensure `pdflatex` is on `PATH`.

Windows example:

```powershell
$env:PATH += ";C:\Program Files\MiKTeX\miktex\bin\x64"
```

### `Input JSON not found`

Check that the path is correct relative to your current working directory, or pass an absolute path.

Examples:

```powershell
.\scripts\build-cv.ps1 -InputJson .\scripts\jimbo-resume.json
.\scripts\build-cv.ps1 -InputJson C:\Users\you\Documents\resume.json
```

### `python-docx not found`

Install it into the same interpreter the build script will use:

```powershell
.\.venv\Scripts\Activate.ps1
pip install python-docx
```

### PDF compilation failed

Check the generated `.tex` file in `formatted/` and rerun `pdflatex` manually if needed:

```powershell
pdflatex -interaction=nonstopmode -output-directory formatted formatted\jhoar-resume.tex
```

## Process-Test Example

`jimbo-resume.json` was added to help test process and documentation rather than resume content.

It intentionally exercises:

- multiple experience entries
- most optional sections
- `section_order`
- `section_filter`
- all supported output formats through `build-cv.ps1`

Use it when you want to validate the pipeline without touching a real resume.
