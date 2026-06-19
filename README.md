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
- [Resume](jhoar-resume.md)
- [Teaching repo](https://github.com/joanne-hoar) - open-source course materials from Robertson College

## Find me

[LinkedIn](https://www.linkedin.com/in/joanne-hoar/) |
[YouTube](https://www.youtube.com/@linuxcodegirl/playlists) |
[GitHub (teaching)](https://github.com/joanne-hoar) |
[Discord: jo.codegirl](https://discordapp.com/users/jo.codegirl) |
[Epic Games](https://store.epicgames.com/u/2c842f1b84774f7f96984af5f9323c65)

## Resume build

This repo uses a public LaTeX template from https://www.latextemplates.com/template/developer-cv.

On Windows, install MiKTeX so `pdflatex` is available on `PATH`.

The main build entrypoint is the PowerShell script in the repo root:

```powershell
.\build-cv.ps1
```

By default, the script looks for exactly one `.json` file in the repo root and uses that as the source data. In this repo, the source file is `jhoar-resume.json`.

The script writes output files beside the input JSON, using the same basename:

- `jhoar-resume.md`
- `jhoar-resume.html`
- `jhoar-resume.txt`
- `jhoar-resume.tex`
- `jhoar-resume.pdf`

You can also pass an explicit input file and output basename:

```powershell
.\build-cv.ps1 -InputJson .\jhoar-resume.json -BaseName jhoar-resume
```

If there are zero or multiple `.json` files in the repo root, pass `-InputJson` explicitly.

If you build from VS Code with LaTeX Workshop, the workspace settings are configured to use `pdflatex` directly instead of `latexmk`.

If MiKTeX is already installed but `pdflatex` is not found, add this folder to your user `PATH`:

`C:\Users\linux\AppData\Local\Programs\MiKTeX\miktex\bin\x64`

Then open a new terminal and verify the install:

```powershell
pdflatex --version
```

The script handles LaTeX include paths for you, so the normal build should be run from the repo root.

If you want to compile the generated `.tex` file manually, build from the repo root and point `TEXINPUTS` at the `latex` folder so `developercv.cls` resolves correctly:

```powershell
$env:TEXINPUTS = (Resolve-Path .\latex).Path + ';'
pdflatex -interaction=nonstopmode -jobname jhoar-resume -output-directory . .\jhoar-resume.tex
```

This direct command writes `jhoar-resume.pdf` to the repo root.

The LaTeX support files and converters live in the `latex/` folder.
