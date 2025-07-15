# Generic Multi-Agent Chatbot Framework

A configurable, generic multi-agent conversational framework designed to be easily customized for any client. This skeleton provides a complete foundation for building professional chatbots with custom branding, agents, tools, and deployment configuration.

## 🚀 Features

- **Generic & Configurable**: No business-specific logic, easily customizable for any use case
- **Multi-Agent Architecture**: Orchestrator with specialized agents and intelligent routing
- **Modern Web Interface**: Responsive UI with role-based interactions and dynamic branding
- **Flexible Tool Integration**: Support for both local and external API tools
- **Easy Deployment**: Docker-ready with comprehensive configuration files
- **Professional Structure**: Clean, documented codebase following best practices

## 📁 Project Structure

```
├── core/                           # Core framework logic
│   ├── config/                     # Configuration management
│   ├── agent/                      # Agent system
│   │   ├── agents/                 # Agent implementations
│   │   ├── tools/                  # Tool management
│   │   └── orchestrator.py         # Main orchestrator
│   └── backend/                    # API backend
├── client_config/                  # Client-specific configuration
│   ├── branding.json               # UI branding and styling
│   ├── agents_config.json          # Agent definitions and routing
│   ├── tools_schema.json           # Available tools configuration
│   ├── entity_patterns.json        # Entity extraction patterns
│   └── reference_map.json          # Reference mappings
├── web/                           # Frontend application
│   ├── static/                    # Static web assets
│   └── main.py                    # Frontend server
├── deployment/                    # Deployment configuration
│   ├── docker-compose.yml         # Docker composition
│   ├── Dockerfile                 # Application container
│   ├── requirements.txt           # Python dependencies
│   └── .env.template              # Environment variables template
├── logs/                          # Application logs
└── docs/                          # Documentation
```

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
