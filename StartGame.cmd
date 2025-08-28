@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem Change to the directory of this script
pushd "%~dp0"

echo === KeyBlaster Launcher ===

rem Detect Python 3 (PATH and common locations)
call :FindPython
if errorlevel 1 (
  echo.
  echo [INFO] Python 3 not found on PATH or standard locations. Attempting automatic install via winget...
  call :InstallPython3
  if errorlevel 1 (
    echo.
    echo [ERROR] Automatic Python installation failed or Python still not available.
    echo         Please install Python 3 from https://www.python.org/downloads/ and re-run this script.
    echo.
    pause
    popd
    endlocal
    exit /b 1
  )
)

rem Create a virtual environment if missing
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment in .venv ...
  %PY% -m venv .venv
  if errorlevel 1 (
    echo.
    echo [ERROR] Failed to create virtual environment.
    echo.
    pause
    popd
    endlocal
    exit /b 1
  )
)

rem Ensure pip is up to date and install dependencies
echo Installing/updating dependencies ...
".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
".venv\Scripts\python.exe" -m pip install --only-binary=:all: -r requirements.txt
if errorlevel 1 (
  echo.
  echo [WARN] Installing from requirements.txt failed. Trying pygame wheel directly...
  ".venv\Scripts\python.exe" -m pip install --only-binary=:all: --upgrade pygame
  if errorlevel 1 (
    echo.
    echo [ERROR] Dependency installation failed.
    echo.
    pause
    popd
    endlocal
    exit /b 1
  )
)

echo.
echo Launching game ...
".venv\Scripts\python.exe" "missile-defence.py"
set EXITCODE=%errorlevel%

echo.
if %EXITCODE% neq 0 (
  echo Game exited with code %EXITCODE%.
) else (
  echo Game closed.
)
echo.
pause

popd
endlocal & exit /b %EXITCODE%

:FindPython
set "PY=py -3"
%PY% -c "import sys; assert sys.version_info[0]==3" >nul 2>&1 && exit /b 0
set "PY=python"
%PY% -c "import sys; assert sys.version_info[0]==3" >nul 2>&1 && exit /b 0

rem Search common install locations
set "CANDIDATE="
for /f "delims=" %%D in ('dir /b /ad /o-n "%LOCALAPPDATA%\Programs\Python\Python3*" 2^>nul') do (
  if exist "%LOCALAPPDATA%\Programs\Python\%%D\python.exe" (
    set "CANDIDATE=%LOCALAPPDATA%\Programs\Python\%%D\python.exe"
    goto :_UseCandidateFind
  )
)
for /f "delims=" %%D in ('dir /b /ad /o-n "%ProgramFiles%\Python3*" 2^>nul') do (
  if exist "%ProgramFiles%\%%D\python.exe" (
    set "CANDIDATE=%ProgramFiles%\%%D\python.exe"
    goto :_UseCandidateFind
  )
)
for /f "delims=" %%D in ('dir /b /ad /o-n "%ProgramFiles(x86)%\Python3*" 2^>nul') do (
  if exist "%ProgramFiles(x86)%\%%D\python.exe" (
    set "CANDIDATE=%ProgramFiles(x86)%\%%D\python.exe"
    goto :_UseCandidateFind
  )
)

exit /b 1

:_UseCandidateFind
set "PY=""%CANDIDATE%"""
%PY% -c "import sys; assert sys.version_info[0]==3" >nul 2>&1 && exit /b 0
exit /b 1

:InstallPython3
rem Try winget for unattended install of Python 3
where winget >nul 2>&1
if errorlevel 1 (
  rem winget not available
  exit /b 1
)

echo.
echo [INFO] Preparing winget sources and trying Python installers...
winget source update >nul 2>&1

rem Try a set of known package IDs (newest first)
set "__PY_IDS=Python.Python.3.13 Python.Python.3.12 Python.Python.3.11 Python.Python.3.10 Python.Python.3 Python.Python"
for %%I in (%__PY_IDS%) do (
  echo [INFO] Attempting: winget install -e --id %%I (silent, user scope)
  winget install -e --id %%I --source winget --scope user --accept-package-agreements --accept-source-agreements --silent
  if not errorlevel 1 goto :PostWingetInstall
)

rem As a last resort, try monikers
for %%M in (python3 python) do (
  echo [INFO] Attempting moniker: winget install %%M (silent, user scope)
  winget install %%M --source winget --scope user --accept-package-agreements --accept-source-agreements --silent
  if not errorlevel 1 goto :PostWingetInstall
)

echo [WARN] winget could not find or install Python packages with known IDs.

goto :DetectAfterInstall

:PostWingetInstall
echo [INFO] winget reported success or partial success. Verifying Python availability...

:DetectAfterInstall
call :FindPython
if errorlevel 1 (
  echo [INFO] Python still not found via PATH or common locations.
  echo [INFO] Attempting direct download from python.org ...
  goto :DirectDownload
)
exit /b 0

:DirectDownload
setlocal
set "DL_DIR=%TEMP%"
set "DL_FILE=%DL_DIR%\python-installer.exe"
if exist "%DL_FILE%" del /q "%DL_FILE%" >nul 2>&1

rem Determine architecture for installer naming
set "__ARCH=amd64"
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "__ARCH=arm64"
if /i "%PROCESSOR_ARCHITECTURE%"=="x86" set "__ARCH="

rem Candidate Python versions to try (adjust over time if needed)
set "__VERS=3.12.5 3.11.9 3.10.14"

for %%V in (%__VERS%) do (
  if defined __ARCH (
    set "__URL=https://www.python.org/ftp/python/%%V/python-%%V-%__ARCH%.exe"
  ) else (
    set "__URL=https://www.python.org/ftp/python/%%V/python-%%V.exe"
  )
  echo [INFO] Downloading Python %%V from: !__URL!
  rem Prefer curl if available
  where curl >nul 2>&1 && (
    curl -L -f -o "%DL_FILE" "!__URL!" 2>nul
  ) || (
    powershell -NoLogo -NoProfile -Command "try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $wc = New-Object System.Net.WebClient; $proxy=[System.Net.WebRequest]::GetSystemWebProxy(); $proxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials; $wc.Proxy = $proxy; $wc.DownloadFile('!__URL!', '%DL_FILE%'); exit 0 } catch { exit 1 }"
  )
  if exist "%DL_FILE%" (
    for %%A in ("%DL_FILE%") do if %%~zA gtr 0 (
      echo [INFO] Running silent installer ...
      "%DL_FILE%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 SimpleInstall=1
      set "__EC=%ERRORLEVEL%"
      if not !__EC! == 0 (
        echo [WARN] Installer returned code !__EC!. Will verify installation.
      )
      del /q "%DL_FILE%" >nul 2>&1
      endlocal & goto :DetectAfterInstall
    )
  )
)

echo [WARN] Could not download Python installer from python.org.
echo [INFO] Opening Python downloads page in your browser...
start "" "https://www.python.org/downloads/windows/"
echo.
echo Please download and install Python 3 (per-user recommended). When finished,
echo return to this window and press any key to continue so we can re-detect.
pause >nul
endlocal & goto :DetectAfterInstall
