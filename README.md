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

```dockerfile
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04
ENV TORCH_DEVICE=cuda
# ... rest van Dockerfile
```

### Cloud Deployment

- **FastMCP Cloud**: Voor MCP server deployment
- **Gradio Spaces**: Voor web interface deployment
- **AWS/GCP/Azure**: Voor volledige container deployment

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
