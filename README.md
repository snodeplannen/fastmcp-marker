# FastMCP Marker - Dual-Interface PDF-to-Markdown Service

Een geavanceerde PDF-naar-Markdown conversie service met dubbele interface: FastMCP voor AI agents en Gradio voor gebruikers. Gebouwd met de krachtige Marker library voor hoogwaardige document intelligentie.

## 🚀 Features

- **Dual Interface**: Zowel MCP server voor AI agents als Gradio web interface voor gebruikers
- **High-Fidelity Conversion**: Gebruikt Marker library voor accurate conversie van complexe documenten
- **Asynchrone Processing**: Non-blocking conversie voor responsieve gebruikerservaring
- **Robuuste Error Handling**: Uitgebreide foutafhandeling met duidelijke feedback
- **Modulaire Architectuur**: Gescheiden concerns voor onderhoudbaarheid en testbaarheid

## 🏗️ Architectuur

Het systeem bestaat uit drie hoofdcomponenten:

1. **`conversion_service.py`** - Core conversie engine met Marker library
2. **`mcp_server.py`** - FastMCP interface voor AI agents
3. **`gradio_app.py`** - Web interface voor gebruikers

## 📋 Vereisten

- Python 3.10+
- uv package manager
- NVIDIA GPU (optioneel, voor betere prestaties)

## 🛠️ Installatie

1. **Clone het project:**
   ```bash
   git clone <repository-url>
   cd fastmcp-marker
   ```

2. **Installeer dependencies met uv:**
   ```bash
   uv sync
   ```

3. **Test de installatie:**
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
- Drag & drop PDF upload
- Real-time conversie progress
- Markdown preview met copy button
- Download geconverteerde bestanden
- Uitgebreide error handling

#### Geavanceerde Interface
Start de uitgebreide interface met alle Marker opties:

```bash
uv run gradio_app_advanced.py
```

**Geavanceerde Features:**
- **Output Formaten**: Markdown, HTML, JSON
- **OCR Instellingen**: Surya/ocrmypdf engines, taal detectie
- **LLM Verbetering**: Gemini API integratie voor hogere nauwkeurigheid
- **Verwerkingsopties**: Pagina bereik, batch processing, VRAM optimalisatie
- **Geavanceerde UI**: Inklapbare instellingen, tabbladen, real-time feedback

### FastMCP Server

Start de MCP server voor AI agents:

```bash
uv run mcp_server.py
```

De server draait op `http://localhost:8000`

**Beschikbare tools:**
- `convert_pdf_to_markdown`: Converteer PDF bytes naar Markdown
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

Run de complete test suite:

```bash
uv run test_system.py
```

Dit test alle componenten:
- Conversion service initialisatie
- MCP server setup
- Gradio app configuratie

## 📁 Project Structuur

```
fastmcp-marker/
├── conversion_service.py      # Core PDF conversie logica met configuratie
├── mcp_server.py             # FastMCP server implementatie
├── gradio_app.py             # Basis Gradio web interface
├── gradio_app_advanced.py    # Geavanceerde Gradio interface
├── windows_fix.py            # Windows multiprocessing fix
├── test_system.py            # Test suite
├── start_service.py          # Interactive startup script
├── main.py                   # Eenvoudige demo
├── pyproject.toml            # Project configuratie
└── README.md                 # Deze documentatie
```

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
```

### Cloud Deployment

- **FastMCP Cloud**: Voor MCP server deployment
- **Gradio Spaces**: Voor web interface deployment
- **AWS/GCP/Azure**: Voor volledige container deployment met GPU ondersteuning

## 🔍 Troubleshooting

### Veelvoorkomende Problemen

1. **Windows Multiprocessing Errors:**
   - Automatisch opgelost met `windows_fix.py` module
   - Stelt threading environment variabelen in
   - Gebruikt 'spawn' multiprocessing methode

2. **Converter initialisatie faalt:**
   - Controleer PyTorch installatie
   - Verificeer GPU drivers (indien GPU gebruikt)

3. **Memory errors:**
   - Verhoog system memory
   - Gebruik CPU-only mode voor kleinere systemen

4. **Slow conversion:**
   - Controleer GPU beschikbaarheid
   - Overweeg OCR disable voor digitale documenten

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
