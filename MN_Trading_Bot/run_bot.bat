@echo off
set USERNAME_PARAM=%~1
set TASK_NAME=%~2
set BOT_DIR=%~3
set PYTHON_EXE=%~4
set SCRIPT_PATH=%~5

cd /d "%BOT_DIR%"

:: 1. Gezieltes Beenden alter Instanzen genau dieser Schedule für diesen User
taskkill /F /FI "USERNAME eq %USERNAME_PARAM%" /FI "WINDOWTITLE eq MN Trading Bot - %TASK_NAME%*" /IM python.exe >nul 2>&1

:: 2. Warten, damit Ressourcen/Ports sauber freigegeben werden (0.5 Sekunde)
timeout /t 1 /nobreak >nul

:: 3. Starten des Bots in einem frischen Konsolenfenster
start "MN Trading Bot - %TASK_NAME%" "%PYTHON_EXE%" -u "%SCRIPT_PATH%" --schedule "%TASK_NAME%"