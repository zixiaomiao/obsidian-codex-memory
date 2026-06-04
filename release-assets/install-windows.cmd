@echo off
setlocal

set "REPO_URL=https://github.com/zixiaomiao/codian.git"
set "PLUGIN_NAME=codian"
set "PLUGIN_DIR=%USERPROFILE%\plugins\%PLUGIN_NAME%"
set "CODEX_HOME=%USERPROFILE%\.codex"
set "SKILL_DIR=%CODEX_HOME%\skills\%PLUGIN_NAME%"
set "MARKETPLACE_PATH=%USERPROFILE%\.agents\plugins\marketplace.json"

where git >nul 2>nul
if errorlevel 1 (
  echo Git is required. Install Git for Windows, then run this installer again.
  echo Download: https://git-scm.com/download/win
  pause
  exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
  echo Python 3 is required. Install Python 3, then run this installer again.
  echo Download: https://www.python.org/downloads/windows/
  pause
  exit /b 1
)

if not exist "%USERPROFILE%\plugins" mkdir "%USERPROFILE%\plugins"

if exist "%PLUGIN_DIR%\.git" (
  echo Updating existing plugin...
  git -C "%PLUGIN_DIR%" pull --ff-only
) else (
  if exist "%PLUGIN_DIR%" (
    echo Plugin directory already exists but is not a Git repository:
    echo %PLUGIN_DIR%
    echo Move that folder aside, then run this installer again.
    pause
    exit /b 1
  )
  echo Downloading plugin...
  git clone "%REPO_URL%" "%PLUGIN_DIR%"
)

if exist "%SKILL_DIR%" rmdir /s /q "%SKILL_DIR%"
if not exist "%CODEX_HOME%\skills" mkdir "%CODEX_HOME%\skills"
xcopy "%PLUGIN_DIR%\skills\%PLUGIN_NAME%" "%SKILL_DIR%\" /E /I /Y >nul

for %%I in ("%MARKETPLACE_PATH%") do if not exist "%%~dpI" mkdir "%%~dpI"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$marketplacePath='%MARKETPLACE_PATH%';" ^
  "$pluginName='%PLUGIN_NAME%';" ^
  "$sourcePath='./plugins/%PLUGIN_NAME%';" ^
  "if (Test-Path $marketplacePath) { $data = Get-Content $marketplacePath -Raw | ConvertFrom-Json } else { $data = [pscustomobject]@{ name='personal'; interface=[pscustomobject]@{ displayName='Personal' }; plugins=@() } };" ^
  "if (-not $data.name) { $data | Add-Member -NotePropertyName name -NotePropertyValue 'personal' -Force };" ^
  "if (-not $data.interface) { $data | Add-Member -NotePropertyName interface -NotePropertyValue ([pscustomobject]@{ displayName='Personal' }) -Force };" ^
  "if (-not $data.plugins) { $data | Add-Member -NotePropertyName plugins -NotePropertyValue @() -Force };" ^
  "$entry = [pscustomobject]@{ name=$pluginName; source=[pscustomobject]@{ source='local'; path=$sourcePath }; policy=[pscustomobject]@{ installation='AVAILABLE'; authentication='ON_INSTALL' }; category='Productivity' };" ^
  "$plugins = @($data.plugins | Where-Object { $_.name -ne $pluginName });" ^
  "$data.plugins = @($plugins + $entry);" ^
  "$data | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 $marketplacePath;" ^
  "Write-Host \"Registered $pluginName in $marketplacePath\""

echo.
echo Installed Codian.
echo Plugin path: %PLUGIN_DIR%
echo Skill path: %SKILL_DIR%
echo.
echo Next step:
echo   Open Codex, enable Codian, then configure your Obsidian vault if needed.
echo.
echo Optional vault config command:
echo   python "%PLUGIN_DIR%\scripts\obsidian_memory.py" init --vault "D:\path\to\your\Obsidian vault"
echo.
pause
