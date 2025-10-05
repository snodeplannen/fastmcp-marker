#!/bin/bash
# FastMCP Marker - Build Virtual Environment Script (Unix/Linux)
# Dit script maakt een venv aan, installeert CUDA PyTorch, en daarna alle dependencies

set -e  # Stop bij eerste fout

echo "========================================"
echo "🚀 FastMCP Marker - Build Environment"
echo "========================================"
echo

# Controleer of uv geïnstalleerd is
if ! command -v uv &> /dev/null; then
    echo "❌ uv package manager niet gevonden!"
    echo "Installeer uv eerst: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv package manager gevonden: $(uv --version)"
echo

# Stap 1: Maak virtual environment aan
echo "📦 Stap 1: Aanmaken virtual environment..."
if ! uv venv; then
    echo "❌ Fout bij aanmaken virtual environment"
    exit 1
fi
echo "✅ Virtual environment aangemaakt"
echo

# Stap 2: Activeer virtual environment
echo "🔧 Stap 2: Activeren virtual environment..."
if ! source .venv/bin/activate; then
    echo "❌ Fout bij activeren virtual environment"
    exit 1
fi
echo "✅ Virtual environment geactiveerd"
echo

# Stap 3: Installeer CUDA PyTorch eerst
echo "🎯 Stap 3: Installeren CUDA PyTorch..."
if ! uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu129; then
    echo "❌ Fout bij installeren CUDA PyTorch"
    exit 1
fi
echo "✅ CUDA PyTorch geïnstalleerd"
echo

# Stap 4: Installeer overige dependencies
echo "📚 Stap 4: Installeren overige dependencies..."
if ! uv sync; then
    echo "❌ Fout bij installeren dependencies"
    exit 1
fi
echo "✅ Alle dependencies geïnstalleerd"
echo

# Stap 5: Verificeer installatie
echo "🧪 Stap 5: Verificatie..."
if ! python -c "import torch; print('✅ PyTorch versie:', torch.__version__); print('✅ CUDA beschikbaar:', torch.cuda.is_available()); print('✅ CUDA versie:', torch.version.cuda if torch.cuda.is_available() else 'N/A')"; then
    echo "❌ Verificatie gefaald"
    exit 1
fi

echo
echo "========================================"
echo "🎉 Build Environment Succesvol!"
echo "========================================"
echo
echo "Om de environment te activeren:"
echo "  source .venv/bin/activate"
echo
echo "Om te testen:"
echo "  uv run test_system.py"
echo

# Maak script executable
chmod +x "$0"
