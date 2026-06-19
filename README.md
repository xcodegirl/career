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
[GitHub (dev)](https://github.com/xcodegirl) |
[Discord: jo.codegirl](https://discordapp.com/users/jo.codegirl) |
[Epic Games](https://store.epicgames.com/u/2c842f1b84774f7f96984af5f9323c65)

## CV Generation

This repo generates professional CVs in **six formats** (PDF, LaTeX, Markdown, HTML, DOCX, TXT) from a single JSON source file, with two style options (article or developer CV).

**→ See [scripts/CV-GENERATION.md](scripts/CV-GENERATION.md) for complete documentation**

### Quick Start

**Windows Explorer:** Double-click `scripts/build-cv.bat` (activates venv automatically)

**PowerShell:**
```powershell
cd scripts
.\build-cv.ps1
```

### Requirements

- Python 3.7+
- MiKTeX or TeX Live (for PDF generation)
- python-docx (for Word documents)

### Virtual Environment

This repo uses a local `.venv` to isolate dependencies:

```powershell
# Auto-detected and used by build scripts
# Or manually activate:
.\.venv\Scripts\Activate.ps1
cd scripts
.\build-cv.ps1
```
