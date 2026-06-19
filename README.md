# Hi, I'm Jo Hoar

<img align="right" src="screenshots/jhoar-profile-small.jpg" width="130" alt="Jo Hoar">

Software developer, game studio co-founder, and online instructor based in Alberta, Canada.

I have been writing software professionally for over twenty years, mostly in C++ and native mobile,
with deep dives into game engines, augmented reality, and scientific computing along the way.
I co-founded two game studios and shipped eleven mobile games to the App Store and Google Play:
2D physics games, ARKit augmented reality apps, sliding-tile puzzles, and a fully 3D open-world
Unreal Engine title.

These days I teach full-stack development and data analytics online at Robertson College while
continuing to build software and explore new tools.

## What I work with

```
C++ / Objective-C / Swift / Kotlin / C# / Java / Python
Unreal Engine / ARKit / SceneKit / OpenGL / Chipmunk
iOS / Android / PlayStation / macOS / Linux / Windows
ASP.NET Core / React / Node.js / Firebase / Azure / Git
```

## Things worth a look

- [Published Games](games-showcase.md) - eleven mobile titles across a decade of indie game dev
- [Work Samples](xcodegirl-work-samples.md) - screenshots and links from across my career
- [Resume](xcodegirl-resume.md)
- [Dev repo](https://github.com/xcodegirl) - pet projects
- [Teaching repo](https://github.com/joanne-hoar) - open-source course materials from Robertson College

## Find me

[LinkedIn](https://www.linkedin.com/in/joanne-hoar/) |
[YouTube](https://www.youtube.com/@linuxcodegirl/playlists) |
[GitHub (teaching)](https://github.com/joanne-hoar) |
[Discord: jo.codegirl](https://discordapp.com/users/jo.codegirl) |
[Epic Games](https://store.epicgames.com/u/2c842f1b84774f7f96984af5f9323c65)

## Multi-format resume generator

This repo generates professional CV/resume documents in six formats from a single JSON source file. It uses a public LaTeX template from [latextemplates.com](https://www.latextemplates.com/template/developer-cv).

### Quick start

**Windows Explorer:** Double-click `scripts/build-cv.bat`

**PowerShell:**
```powershell
cd scripts
.\build-cv.ps1
```

### How it works

1. Edit `scripts/jhoar-resume.json` with your resume data
2. Run the build script
3. All formats are generated to `formatted/`

### Output formats

- **Markdown** (`*.md`) — Clean, portable format
- **HTML** (`*.html`) — Self-contained single file with embedded CSS
- **Plain text** (`*.txt`) — No formatting
- **LaTeX** (`*.tex`) — Source code for PDF compilation
- **PDF** (`*.pdf`) — Print-ready document
- **Word** (`*.docx`) — Editable Microsoft Word document

### Requirements

| Tool | Purpose | Install |
|------|---------|---------|
| Python 3.7+ | Run build scripts | [python.org](https://python.org) |
| python-docx | Generate Word documents | `pip install python-docx` |
| MiKTeX or TeX Live | PDF generation | [miktex.org](https://miktex.org) or [tug.org](https://tug.org/texlive) |

**Verify installation:**
```powershell
python --version
pip show python-docx
pdflatex --version
```

### Advanced: Manual PDF compilation

To compile the LaTeX source directly:
```powershell
cd formatted
$env:TEXINPUTS = (Resolve-Path ..\scripts).Path + ';'
pdflatex -interaction=nonstopmode jhoar-resume.tex
```

### Customizing the resume

Edit `scripts/jhoar-resume.json` with sections for:
- Contact (LinkedIn, GitHub)
- Summary
- Experience (with dates, companies, descriptions, and technologies)
- Education
- Awards & honors
- Languages
- Portfolio links
- Published games (if applicable)

The build system handles formatting—just provide clean data.
