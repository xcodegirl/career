@echo off
REM Build CV from JSON - activates virtual environment and runs PowerShell build script.
REM Double-click this file to generate all CV formats.

setlocal enabledelayedexpansion

set VENV_DIR=%~dp0..\\.venv

if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "%VENV_DIR%\Scripts\activate.bat"
) else (
    echo Warning: Virtual environment not found at %VENV_DIR%
    echo Proceeding without virtual environment activation...
)

echo.
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
