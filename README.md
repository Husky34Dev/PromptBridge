
# PromptBridge: Flexible Multi-Agent Chatbot Framework

PromptBridge es un framework conversacional multi-agente, altamente configurable y orientado a despliegues profesionales. Permite crear asistentes virtuales con lógica flexible, integración de herramientas externas, branding personalizado y despliegue sencillo.

## Características principales

- Arquitectura multi-agente con orquestador y agentes especializados
- Contexto conversacional y modos de operación configurables
- Integración de herramientas vía API y lógica local
- Frontend web moderno y personalizable
- Configuración por archivos JSON para clientes, branding y herramientas
- Listo para despliegue en Docker y entornos cloud

## Estructura del proyecto

```
├── core/
│   ├── config/               # Configuración global y utilidades
│   ├── agent/                # Orquestador, agentes y middleware
│   │   ├── agents/           # Implementaciones de agentes
│   │   ├── tools/            # Lógica de herramientas
│   │   └── orchestrator.py   # Orquestador principal
│   └── backend/              # API REST y base de datos
├── client_config/            # Configuración específica de cliente
│   ├── branding.json         # Branding y estilos UI
│   ├── agents_config.json    # Definición de agentes
│   ├── tools_schema.json     # Herramientas disponibles
│   ├── entity_patterns.json  # Patrones de entidades
│   └── reference_map.json    # Mapeo de referencias
├── web/
│   ├── static/               # Frontend web (JS, CSS, HTML)
│   └── main.py               # Servidor FastAPI para frontend
├── deployment/               # Docker, requirements, .env
├── logs/                     # Logs de aplicación
└── docs/                     # Documentación técnica
```

## Instalación rápida

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Husky34Dev/PromptBridge.git
   cd PromptBridge
   ```
2. Instala dependencias:
   ```bash
   pip install -r deployment/requirements.txt
   ```
3. Configura los archivos en `client_config/` según tu caso de uso.
4. Ejecuta el backend y frontend:
   ```bash
   python -m core.backend.server
   python web/main.py
   ```
5. Accede a la interfaz en `http://localhost:8080`

## Personalización

- Modifica `branding.json` para adaptar colores, logo y nombre de empresa.
- Define agentes y herramientas en `agents_config.json` y `tools_schema.json`.
- Extiende la lógica de agentes en `core/agent/agents/` y herramientas en `core/agent/tools/`.
- Añade endpoints o lógica de negocio en `core/backend/server.py`.

## Despliegue en Docker

```bash
docker-compose up --build
```
Configura variables en `.env.template` y adapta los archivos de despliegue según tu entorno.

## API principal

- `POST /api/chat` — Consulta principal del chatbot
- `GET /api/branding` — Configuración visual
- `GET /api/health` — Health check

## Contribución y soporte

¿Quieres colaborar? Haz un fork, crea tu rama y envía un pull request. Para soporte, abre un issue en GitHub.

---

PromptBridge es ideal para empresas que buscan asistentes virtuales flexibles, seguros y personalizables. ¡Listo para producción y fácil de adaptar a cualquier cliente!

## 🛠️ Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd agente-groq-

# Copy environment template
cp deployment/.env.template .env

# Edit .env with your API keys and configuration
```

### 2. Install Dependencies

```bash
pip install -r deployment/requirements.txt
```

### 3. Configure Your Chatbot

Edit the configuration files in `client_config/`:

- `branding.json`: Customize colors, logo, company name
- `agents_config.json`: Define your agents and their capabilities
- `tools_schema.json`: Configure available tools and integrations

### 4. Run the Application

```bash
# Start backend API
python -m core.backend.server

# In another terminal, start frontend
python -m web.main
```

Visit `http://localhost:3000` to interact with your chatbot.

### 5. Docker Deployment

```bash
# Build and run with Docker
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

## ⚙️ Configuration Guide

### Branding Customization

Edit `client_config/branding.json`:

```json
{
  "company_name": "Your Company",
  "primary_color": "#your-color",
  "secondary_color": "#your-secondary",
  "logo_path": "/static/assets/your-logo.png"
}
```

### Agent Configuration

Define your agents in `client_config/agents_config.json`:

```json
{
  "agents": [
    {
      "name": "support_agent",
      "description": "Handles customer support queries",
      "system_prompt": "You are a helpful support agent...",
      "tools": ["knowledge_search", "ticket_creation"]
    }
  ]
}
```

### Tool Integration

Configure tools in `client_config/tools_schema.json`:

```json
{
  "tools": [
    {
      "name": "api_tool",
      "type": "api",
      "endpoint": "https://your-api.com/endpoint",
      "description": "Calls external API"
    }
  ]
}
```

## 🔧 Customization

### Adding New Agents

1. Create agent configuration in `agents_config.json`
2. Implement specific logic in `core/agent/agents/` if needed
3. Update routing rules in the orchestrator

### Adding New Tools

1. Define tool schema in `tools_schema.json`
2. Implement tool logic in `core/agent/tools/`
3. Register tool with the tool manager

### Frontend Customization

- Modify `web/static/index.html` for structure changes
- Update `web/static/styles.css` for styling
- Extend `web/static/app.js` for functionality

## 🚢 Deployment

### Environment Variables

Configure these in your `.env` file:

```env
# API Configuration
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-key

# Server Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Database (if needed)
DATABASE_URL=your-database-url
```

### Production Deployment

1. Configure your production environment variables
2. Update `docker-compose.yml` for production settings
3. Deploy using Docker or your preferred platform

```bash
# Production build
docker-compose -f docker-compose.prod.yml up -d
```

## 📖 API Reference

### Chat Endpoint

```http
POST /api/chat
Content-Type: application/json

{
  "message": "User message",
  "user_role": "client",
  "context": {}
}
```

### Configuration Endpoints

- `GET /api/branding` - Get branding configuration
- `GET /api/agents` - Get available agents
- `GET /api/health` - Health check

## 🧪 Development

### Running Tests

```bash
# Run tests (when implemented)
python -m pytest tests/
```

### Development Mode

```bash
# Run with hot reload
uvicorn core.backend.server:app --reload --port 8000
uvicorn web.main:app --reload --port 3000
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Check the documentation in `docs/`
- Open an issue on GitHub
- Contact: support@yourcompany.com

---

**Ready to build your custom chatbot?** Start by configuring the files in `client_config/` and you'll have a professional chatbot running in minutes!
