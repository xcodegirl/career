@echo off
setlocal enabledelayedexpansion

REM PowerShell script wrapper for build-cv.ps1
REM Double-click this file to build all CV formats

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build-cv.ps1"

if !errorlevel! neq 0 (
    echo.
    echo Build failed with error code !errorlevel!
    pause
) else (
    echo.
    echo Build completed successfully!
    echo Output is in: "%~dp0..\formatted\"
    pause
)

endlocal
