@echo off
REM Backend setup script for pre-processing service (Windows)
setlocal enabledelayedexpansion

echo 🔧 Setting up Pre-processing Service...
cd /d "%~dp0"

if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

echo ✨ Activating virtual environment...
call venv\Scripts\activate.bat

echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo 📚 Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo ✅ Pre-processing service setup complete!
echo 📝 To activate the environment, run: venv\Scripts\activate.bat
pause
