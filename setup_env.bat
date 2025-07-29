@echo off
setlocal

set VENV_NAME=venv

REM --- Vérifie si Python 3.11 est disponible via py launcher ---
py -3.11 --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python 3.11 n'est pas installé ou non disponible via 'py -3.11'.
    echo ▶️ Assure-toi d'avoir installé Python 3.11 depuis : https://www.python.org/downloads/release/python-3110/
    pause
    exit /b
)

REM --- Crée l'environnement virtuel s'il n'existe pas ---
if not exist %VENV_NAME% (
    echo ✅ Création de l'environnement virtuel avec Python 3.11...
    py -3.11 -m venv %VENV_NAME%
)

REM --- Active l'environnement virtuel ---
call %VENV_NAME%\Scripts\activate.bat

REM --- Met à jour pip ---
python -m pip install --upgrade pip

REM --- Installer les dépendances ---
echo ✅ Installation des dépendances...
pip install flask pandas

REM --- Lancer l'application Flask ---
echo 🚀 Lancement de l'application Flask...
python visualisation.py

pause
