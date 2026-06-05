@echo off
setlocal

set "REPO_URL=https://github.com/zixiaomiao/codian.git"
set "PLUGIN_NAME=codin"
set "CODEX_HOME=%USERPROFILE%\.codex"
set "SKILL_DIR=%CODEX_HOME%\skills\%PLUGIN_NAME%"
set "GITHUB_DIR=%CODEX_HOME%\skills\%PLUGIN_NAME% GitHub"
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

if not exist "%CODEX_HOME%\skills" mkdir "%CODEX_HOME%\skills"

if exist "%GITHUB_DIR%\.git" (
  echo Updating existing plugin...
  git -C "%GITHUB_DIR%" pull --ff-only
) else (
  if exist "%GITHUB_DIR%" (
    echo Refreshing existing plugin directory...
    rmdir /s /q "%GITHUB_DIR%"
  )
  echo Downloading plugin...
  git clone "%REPO_URL%" "%GITHUB_DIR%"
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$githubDir='%GITHUB_DIR%';" ^
  "$skillDir='%SKILL_DIR%';" ^
  "if (Test-Path $skillDir) { Remove-Item -Recurse -Force $skillDir };" ^
  "New-Item -ItemType Directory -Force -Path $skillDir | Out-Null;" ^
  "$items = @('SKILL.md','scripts','references','assets','agents');" ^
  "foreach ($item in $items) { $src = Join-Path $githubDir $item; if (Test-Path $src) { Copy-Item $src -Destination $skillDir -Recurse -Force } }"

for %%I in ("%MARKETPLACE_PATH%") do if not exist "%%~dpI" mkdir "%%~dpI"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$marketplacePath='%MARKETPLACE_PATH%';" ^
  "$pluginName='%PLUGIN_NAME%';" ^
  "$sourcePath='%SKILL_DIR%';" ^
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
echo Installed Codin.
echo Skill path: %SKILL_DIR%
echo GitHub copy: %GITHUB_DIR%
echo.
echo Next step:
echo   Open Codex, enable Codin, then configure your Obsidian vault if needed.
echo.
echo Optional vault config command:
echo   python "%SKILL_DIR%\scripts\obsidian_memory.py" init --vault "D:\path\to\your\Obsidian vault"
echo.
pause
