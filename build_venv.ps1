# FastMCP Marker - Build Virtual Environment Script (PowerShell)
# Dit script maakt een venv aan, installeert CUDA PyTorch, en daarna alle dependencies

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 FastMCP Marker - Build Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Controleer of uv geïnstalleerd is
try {
    $uvVersion = uv --version
    Write-Host "✅ uv package manager gevonden: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ uv package manager niet gevonden!" -ForegroundColor Red
    Write-Host "Installeer uv eerst: https://astral.sh/uv/install.sh" -ForegroundColor Yellow
    Read-Host "Druk Enter om af te sluiten"
    exit 1
}

Write-Host ""

# Stap 1: Maak virtual environment aan
Write-Host "📦 Stap 1: Aanmaken virtual environment..." -ForegroundColor Yellow
try {
    uv venv
    Write-Host "✅ Virtual environment aangemaakt" -ForegroundColor Green
} catch {
    Write-Host "❌ Fout bij aanmaken virtual environment" -ForegroundColor Red
    Read-Host "Druk Enter om af te sluiten"
    exit 1
}

Write-Host ""

# Stap 2: Activeer virtual environment
Write-Host "🔧 Stap 2: Activeren virtual environment..." -ForegroundColor Yellow
try {
    & .\.venv\Scripts\Activate.ps1
    Write-Host "✅ Virtual environment geactiveerd" -ForegroundColor Green
} catch {
    Write-Host "❌ Fout bij activeren virtual environment" -ForegroundColor Red
    Write-Host "Mogelijk moet je execution policy aanpassen:" -ForegroundColor Yellow
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Read-Host "Druk Enter om af te sluiten"
    exit 1
}

Write-Host ""

# Stap 3: Installeer CUDA PyTorch eerst
Write-Host "🎯 Stap 3: Installeren CUDA PyTorch..." -ForegroundColor Yellow
try {
    uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu129
    Write-Host "✅ CUDA PyTorch geïnstalleerd" -ForegroundColor Green
} catch {
    Write-Host "❌ Fout bij installeren CUDA PyTorch" -ForegroundColor Red
    Read-Host "Druk Enter om af te sluiten"
    exit 1
}

Write-Host ""

# Stap 4: Installeer overige dependencies
Write-Host "📚 Stap 4: Installeren overige dependencies..." -ForegroundColor Yellow
try {
    uv sync
    Write-Host "✅ Alle dependencies geïnstalleerd" -ForegroundColor Green
} catch {
    Write-Host "❌ Fout bij installeren dependencies" -ForegroundColor Red
    Read-Host "Druk Enter om af te sluiten"
    exit 1
}

Write-Host ""

# Stap 5: Verificeer installatie
Write-Host "🧪 Stap 5: Verificatie..." -ForegroundColor Yellow
try {
    $pythonOutput = python -c "import torch; print('✅ PyTorch versie:', torch.__version__); print('✅ CUDA beschikbaar:', torch.cuda.is_available()); print('✅ CUDA versie:', torch.version.cuda if torch.cuda.is_available() else 'N/A')"
    Write-Host $pythonOutput -ForegroundColor Green
} catch {
    Write-Host "❌ Verificatie gefaald" -ForegroundColor Red
    Read-Host "Druk Enter om af te sluiten"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 Build Environment Succesvol!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Om de environment te activeren:" -ForegroundColor Yellow
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Om te testen:" -ForegroundColor Yellow
Write-Host "  uv run test_system.py" -ForegroundColor White
Write-Host ""

Read-Host "Druk Enter om af te sluiten"
