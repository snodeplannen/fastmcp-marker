# FastMCP Marker - Dual-Interface PDF-to-Markdown Service

Een geavanceerde PDF-naar-Markdown conversie service met dubbele interface: FastMCP voor AI agents en Gradio voor gebruikers. Gebouwd met de krachtige Marker library voor hoogwaardige document intelligentie.

## 🚀 Features

- **Dual Interface**: Zowel MCP server voor AI agents als Gradio web interface voor gebruikers
- **ZIP Output**: Alle gegenereerde bestanden worden automatisch verpakt in een ZIP-bestand
- **Batch Processing**: Ondersteuning voor meerdere PDF's tegelijkertijd met georganiseerde output
- **High-Fidelity Conversion**: Gebruikt Marker library voor accurate conversie van complexe documenten
- **Asynchrone Processing**: Non-blocking conversie voor responsieve gebruikerservaring
- **Robuuste Error Handling**: Uitgebreide foutafhandeling met duidelijke feedback
- **Progress Tracking**: Real-time voortgangsindicatie voor batch-verwerking
- **Geünificeerde Architectuur**: Alle conversie functionaliteit in één service voor betere performance
- **Autonome Testing**: Volledig geautomatiseerde test suite met server management
- **Cross-Platform**: Werkt stabiel op Windows, Linux en macOS zonder platform-specifieke fixes

## 📦 ZIP Output Functionaliteit

De applicatie genereert nu automatisch ZIP-bestanden met alle gegenereerde content:

### Wat wordt opgenomen in het ZIP-bestand:
- **Geconverteerde tekst**: Markdown, HTML of JSON output
- **Geëxtraheerde afbeeldingen**: Alle afbeeldingen uit het PDF (indien geactiveerd)
- **Debug bestanden**: Layout images, JSON data, en andere debug informatie (indien geactiveerd)
- **Overzicht**: Gestructureerd overzicht van alle conversies

### ZIP Structuur:
```
conversie_resultaten.zip
├── 00_OVERVIEW.md                    # Overzicht van alle conversies
├── 01_document1/
│   ├── converted_text.md             # Hoofdtekst
│   ├── output/                       # Alle output bestanden
│   ├── images/                       # Geëxtraheerde afbeeldingen
│   └── debug/                        # Debug bestanden
└── 02_document2/
    ├── converted_text.md
    ├── output/
    ├── images/
    └── debug/
```

### UI Instellingen:
- **Inclusief Afbeeldingen in ZIP**: Controleer of afbeeldingen worden opgenomen
- **Inclusief Debug Bestanden in ZIP**: Controleer of debug data wordt opgenomen
- **Preview**: Bekijk de geconverteerde tekst direct in de interface
- **Download**: Download het volledige ZIP-bestand met alle bestanden

## 🏗️ Architectuur

Het systeem bestaat uit drie hoofdcomponenten:

1. **`conversion_service.py`** - Geünificeerde conversie engine met ZIP output functionaliteit
2. **`mcp_server.py`** - FastMCP interface voor AI agents
3. **`gradio_app_advanced_full.py`** - Geavanceerde web interface met ZIP output

### Vereenvoudigde Architectuur
- **Geünificeerde service**: Alle conversie functionaliteit in één module
- **Geen Windows fixes**: Moderne PyTorch/Marker versies werken stabiel zonder workarounds
- **Geen subprocess overhead**: Directe conversie zonder complexe subprocess communicatie
- **Betere performance**: Minder overhead en snellere conversie

## 📋 Vereisten

- Python 3.12+
- uv package manager
- NVIDIA GPU (optioneel, voor betere prestaties)
- Ollama (voor LLM functionaliteit)

## 🛠️ Development Setup

### DevContainer (Aanbevolen)

Voor een consistente development environment met CUDA ondersteuning:

1. **Open in VS Code/Cursor:**
   ```bash
   code .
   ```

2. **Reopen in Container:**
   - Druk `Ctrl+Shift+P` (of `Cmd+Shift+P` op Mac)
   - Selecteer "Dev Containers: Reopen in Container"
   - Wacht tot de container is gebouwd en gestart

3. **Development features:**
   - ✅ CUDA/cuDNN ondersteuning
   - ✅ Alle Python dependencies geïnstalleerd
   - ✅ VS Code extensions geconfigureerd
   - ✅ Port forwarding (8000, 7860)
   - ✅ Volume mounts voor data/output/logs
   - ✅ Interactive bash shell

### Lokale Development

#### Automatische Build Scripts (Aanbevolen)

Voor een correcte installatie met CUDA PyTorch ondersteuning:

**Windows Command Prompt:**
```cmd
build_venv.cmd
```

**Windows PowerShell:**
```powershell
.\build_venv.ps1
```

**Unix/Linux/macOS:**
```bash
./build_venv.sh
```

> **💡 Waarom deze scripts?** Ze zorgen ervoor dat CUDA PyTorch wordt geïnstalleerd voordat andere dependencies, wat voorkomt dat de CPU-versie wordt geïnstalleerd.

#### Handmatige Installatie

1. **Clone het project:**
   ```bash
   git clone <repository-url>
   cd fastmcp-marker
   ```

2. **Maak virtual environment:**
   ```bash
   uv venv
   ```

3. **Activeer environment:**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Unix/Linux/macOS
   source .venv/bin/activate
   ```

4. **Installeer CUDA PyTorch eerst:**
   ```bash
   uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu129
   ```

5. **Installeer overige dependencies:**
   ```bash
   uv sync
   ```

6. **Test de installatie:**
   ```bash
   uv run test_system.py
   ```

## 🚀 Gebruik

### Gradio Web Interfaces

#### Basis Interface
Start de basis web interface voor gebruikers:

```bash
uv run gradio_app.py
```

**Features:**
- Drag & drop PDF upload (enkele of meerdere bestanden)
- Batch processing met real-time voortgangsindicatie
- Markdown preview met copy button
- ZIP download voor batch-resultaten
- Uitgebreide error handling per bestand

#### Geavanceerde Interface
Start de uitgebreide interface met alle Marker opties en ZIP output:

```bash
uv run gradio_app_advanced_full.py
```

**Geavanceerde Features:**
- **ZIP Output**: Alle gegenereerde bestanden automatisch verpakt in ZIP
- **Output Formaten**: Markdown, HTML, JSON
- **OCR Instellingen**: Surya/ocrmypdf engines, taal detectie
- **LLM Verbetering**: Gemini, OpenAI, Anthropic, Azure, Ollama ondersteuning
- **Batch Processing**: Meerdere PDF's tegelijkertijd met georganiseerde ZIP output
- **Debug Functionaliteit**: Layout images, JSON data, debug bestanden
- **ZIP Instellingen**: Controleer wat er wordt opgenomen in het ZIP-bestand
- **Verwerkingsopties**: Pagina bereik, batch processing, VRAM optimalisatie
- **Geavanceerde UI**: Inklapbare instellingen, tabbladen, real-time feedback

### FastMCP Server

Start de MCP server voor AI agents:

```bash
uv run mcp_server.py
```

De server draait op `http://localhost:8000`

**Beschikbare tools:**
- `convert_pdf_to_markdown`: Converteer enkele PDF bytes naar Markdown
- `convert_multiple_pdfs_to_markdown`: Batch conversie van meerdere PDF's
- `get_converter_status`: Controleer converter status

### MCP Client Integratie

Voor gebruik met AI agents (bijvoorbeeld in Cursor):

```json
{
  "mcpServers": {
    "pdf-converter": {
      "command": "uv",
      "args": ["run", "mcp_server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## 🧪 Testing

### Complete Test Suite

Run alle tests om de volledige functionaliteit te verifiëren:

```bash
# Test unified conversion service
uv run tests/test_unified_service.py

# Test ZIP conversion functionality
uv run tests/test_zip_conversion.py

# Test worker configuration
uv run tests/test_worker_config.py

# Test Gradio API (autonomous server management)
uv run tests/test_gradio_api_extended.py

# Test direct conversion
uv run test_conversion_direct.py
```

### Test Organisatie

Tests zijn georganiseerd in de `tests/` directory:
- **`test_unified_service.py`** - Test de geünificeerde conversion service
- **`test_zip_conversion.py`** - Test ZIP output functionaliteit
- **`test_worker_config.py`** - Test worker configuration override
- **`test_gradio_api_extended.py`** - Test Gradio API met autonome server management

### Test Files

Test PDF bestanden zijn opgeslagen in `testfiles/`:
- **`test_document.pdf`** - Kleine test PDF voor snelle tests
- **`testdocument2.pdf`** - Grotere test PDF voor uitgebreide tests

### Autonome Testing

De Gradio API test (`test_gradio_api_extended.py`) is volledig autonoom:
- Detecteert automatisch of Gradio server draait
- Start server indien nodig (met 60s timeout voor model loading)
- Voert alle tests uit
- Ruimt automatisch op na afloop

## 📁 Project Structuur

```
fastmcp-marker/
├── conversion_service.py           # Geünificeerde PDF conversie service
├── mcp_server.py                  # FastMCP server implementatie
├── gradio_app_advanced_full.py    # Geavanceerde Gradio web interface
├── test_conversion_direct.py      # Directe conversie test
├── test_windows_fixes.py          # Windows fixes verificatie test
├── tests/                         # Test directory
│   ├── test_unified_service.py    # Unified service tests
│   ├── test_zip_conversion.py     # ZIP conversion tests
│   ├── test_worker_config.py      # Worker config tests
│   └── test_gradio_api_extended.py # Gradio API tests
├── testfiles/                     # Test PDF bestanden
│   ├── test_document.pdf          # Kleine test PDF
│   └── testdocument2.pdf          # Grotere test PDF
├── pyproject.toml                 # Project configuratie
└── README.md                      # Deze documentatie
```

### Belangrijke Wijzigingen

- **Geünificeerde architectuur**: Alle conversie functionaliteit in één service
- **Georganiseerde tests**: Tests in `tests/` directory met duidelijke structuur
- **Test files**: PDF bestanden in `testfiles/` directory
- **Verwijderde bestanden**: Oude services en Windows fixes niet meer nodig

## ⚡ Performance

- **GPU Acceleratie**: Automatische detectie van NVIDIA GPU voor snellere conversie
- **Asynchrone Processing**: Non-blocking conversie met `asyncio.to_thread`
- **Resource Management**: Efficiënte geheugenbeheer voor grote documenten

## 🔧 Configuratie

### Environment Variables

```bash
# Voor GPU ondersteuning
export TORCH_DEVICE=cuda

# Voor CPU-only mode
export TORCH_DEVICE=cpu
```

### Marker Library Opties

De Marker library ondersteunt verschillende configuratie opties voor optimalisatie:

- OCR disable voor digitale documenten
- Parallel processing voor batch conversies
- Custom model paths

## 🚀 Deployment

### Docker Deployment

Het project bevat volledige Docker ondersteuning met CUDA/cuDNN voor GPU acceleratie.

#### Vereisten
- Docker met NVIDIA Container Toolkit
- NVIDIA GPU met CUDA ondersteuning (optioneel)
- Ollama draaiend op localhost:11434

> **💡 Ollama Setup**: Zorg ervoor dat Ollama draait op je lokale machine voordat je Docker start. De containers kunnen Ollama bereiken via `host.docker.internal:11434`.

#### Snelle Start

1. **Start GPU versie (standaard):**
   ```bash
   docker-compose up --build
   ```

2. **CPU-only mode (zonder GPU):**
   ```bash
   docker-compose --profile cpu-only up
   ```

> **💡 Tip**: Standaard wordt alleen de GPU versie gestart. De CPU fallback wordt alleen gestart wanneer je expliciet `--profile cpu-only` gebruikt.

#### Services en Poorten

- **MCP Server**: `http://localhost:8000` (GPU) / `http://localhost:8001` (CPU)
- **Gradio Web**: `http://localhost:7860` (GPU) / `http://localhost:7861` (CPU)

> **💡 Tip**: De Docker image start automatisch beide services tegelijkertijd via het `start_services.sh` script.

#### Docker Commands

```bash
# Build image
docker build -t fastmcp-marker .

# Run both services (MCP + Gradio)
docker run --gpus all -p 8000:8000 -p 7860:7860 fastmcp-marker

# CPU-only mode
docker run -e TORCH_DEVICE=cpu -p 8000:8000 -p 7860:7860 fastmcp-marker
```

#### Volume Mounts

De Docker containers mounten de volgende directories:
- `./data` → `/app/data` (input PDFs)
- `./output` → `/app/output` (geconverteerde bestanden)
- `./logs` → `/app/logs` (log bestanden)

#### Environment Variables

```bash
# GPU configuratie
TORCH_DEVICE=cuda
CUDA_VISIBLE_DEVICES=0

# CPU-only mode
TORCH_DEVICE=cpu

# Ollama integratie
OLLAMA_HOST=host.docker.internal:11434
```

#### Ollama Integratie

De Docker containers zijn geconfigureerd om toegang te hebben tot je lokale Ollama server:

1. **Start Ollama lokaal:**
   ```bash
   ollama serve
   ```

2. **Test Ollama verbinding vanuit container:**
   ```bash
   docker exec -it fastmcp-marker curl http://host.docker.internal:11434/api/tags
   ```

3. **Configureer Ollama model:**
   ```bash
   ollama pull llama3.2  # of een ander model
   ```

### Cloud Deployment

- **FastMCP Cloud**: Voor MCP server deployment
- **Gradio Spaces**: Voor web interface deployment
- **AWS/GCP/Azure**: Voor volledige container deployment met GPU ondersteuning

## 🔍 Troubleshooting

### Veelvoorkomende Problemen

1. **Converter initialisatie faalt:**
   - Controleer PyTorch installatie
   - Verificeer GPU drivers (indien GPU gebruikt)
   - Moderne PyTorch/Marker versies werken stabiel zonder Windows fixes

2. **Memory errors:**
   - Verhoog system memory
   - Gebruik CPU-only mode voor kleinere systemen

3. **Slow conversion:**
   - Controleer GPU beschikbaarheid
   - Overweeg OCR disable voor digitale documenten

4. **Test failures:**
   - Zorg dat test PDF bestanden in `testfiles/` directory staan
   - Run tests vanuit project root directory
   - Voor Gradio API tests: server wordt automatisch gestart indien nodig

### Docker-specifieke Problemen

1. **NVIDIA Container Toolkit niet geïnstalleerd:**
   ```bash
   # Ubuntu/Debian
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   ```

2. **CUDA niet beschikbaar in container:**
   ```bash
   # Test CUDA beschikbaarheid
   docker run --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi
   ```

3. **Container start niet:**
   - Controleer poort beschikbaarheid: `netstat -tulpn | grep :8000`
   - Gebruik CPU-only mode als fallback: `docker-compose --profile cpu-only up`

4. **Build faalt:**
   - Verhoog Docker memory limit
   - Gebruik `--no-cache` flag: `docker-compose build --no-cache`

### DevContainer-specifieke Problemen

1. **DevContainer start niet:**
   - Controleer NVIDIA Container Toolkit: `docker run --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi`
   - Herstart Docker Desktop
   - Gebruik "Dev Containers: Rebuild Container"

2. **CUDA niet beschikbaar in DevContainer:**
   - Controleer `runArgs` in devcontainer.json
   - Verificeer GPU beschikbaarheid: `nvidia-smi`
   - Herstart de DevContainer

3. **Port forwarding werkt niet:**
   - Controleer poort configuratie in devcontainer.json
   - Gebruik "Ports" tab in VS Code
   - Handmatig forwarden: `uv run mcp_server.py`

4. **Extensions niet geïnstalleerd:**
   - Herstart VS Code/Cursor
   - Gebruik "Dev Containers: Rebuild Container"
   - Controleer extensions in devcontainer.json

5. **Ollama niet bereikbaar vanuit container:**
   - Controleer of Ollama draait: `ollama list`
   - Test lokale verbinding: `curl http://localhost:11434/api/tags`
   - Controleer Docker host gateway: `docker exec -it container ping host.docker.internal`
   - Herstart Docker Desktop

### Logs

Alle componenten loggen uitgebreide informatie naar console voor debugging.

## 🤝 Contributing

1. Fork het project
2. Maak een feature branch
3. Commit je changes
4. Push naar de branch
5. Open een Pull Request

## 📄 License

Dit project is gelicenseerd onder de MIT License.

## 🙏 Acknowledgments

- [Marker](https://github.com/datalab-to/marker) - Voor hoogwaardige PDF conversie
- [FastMCP](https://github.com/jlowin/fastmcp) - Voor MCP server framework
- [Gradio](https://gradio.app/) - Voor web interface framework
