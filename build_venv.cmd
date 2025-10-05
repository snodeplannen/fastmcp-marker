@echo off
REM FastMCP Marker - Build Virtual Environment Script (Windows CMD)
REM Dit script maakt een venv aan, installeert CUDA PyTorch, en daarna alle dependencies

echo ========================================
echo 🚀 FastMCP Marker - Build Environment
echo ========================================
echo.

REM Controleer of uv geïnstalleerd is
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ uv package manager niet gevonden!
    echo Installeer uv eerst: https://astral.sh/uv/install.sh
    pause
    exit /b 1
)

echo ✅ uv package manager gevonden: 
uv --version
echo.

REM Stap 1: Maak virtual environment aan
echo 📦 Stap 1: Aanmaken virtual environment...
uv venv
if %errorlevel% neq 0 (
    echo ❌ Fout bij aanmaken virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment aangemaakt
echo.

REM Stap 2: Activeer virtual environment
echo 🔧 Stap 2: Activeren virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Fout bij activeren virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment geactiveerd
echo.

REM Stap 3: Installeer CUDA PyTorch eerst
echo 🎯 Stap 3: Installeren CUDA PyTorch...
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu129
if %errorlevel% neq 0 (
    echo ❌ Fout bij installeren CUDA PyTorch
    pause
    exit /b 1
)
echo ✅ CUDA PyTorch geïnstalleerd
echo.

REM Stap 4: Installeer overige dependencies
echo 📚 Stap 4: Installeren overige dependencies...
uv sync
if %errorlevel% neq 0 (
    echo ❌ Fout bij installeren dependencies
    pause
    exit /b 1
)
echo ✅ Alle dependencies geïnstalleerd
echo.

REM Stap 5: Verificeer installatie
echo 🧪 Stap 5: Verificatie...
python -c "import torch; print('✅ PyTorch versie:', torch.__version__); print('✅ CUDA beschikbaar:', torch.cuda.is_available()); print('✅ CUDA versie:', torch.version.cuda if torch.cuda.is_available() else 'N/A')"
if %errorlevel% neq 0 (
    echo ❌ Verificatie gefaald
    pause
    exit /b 1
)

echo.
echo ========================================
echo 🎉 Build Environment Succesvol!
echo ========================================
echo.
echo Om de environment te activeren:
echo   .venv\Scripts\activate.bat
echo.
echo Om te testen:
echo   uv run test_system.py
echo.
pause
