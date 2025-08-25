# Vanna AI FastAPI Backend

FastAPI backend for Vanna AI integration with Open WebUI, enabling natural language SQL queries through a web interface.

## Overview

This project provides a FastAPI backend that integrates Vanna AI with Open WebUI. Users can ask questions in natural language and get SQL queries generated from their database, along with results and visualizations.

**Components:**

- **FastAPI Backend**: REST API for Vanna AI operations
- **Vanna AI**: Text-to-SQL using RAG with ChromaDB
- **Open WebUI**: Web interface for chat-like interactions
- **Ollama**: Local LLM server for query processing

## Project Structure

```
.
├── app/
│   ├── api/routes/
│   │   ├── data.py
│   │   ├── questions.py
│   │   ├── sql.py
│   │   └── training.py
│   ├── config.py
│   ├── main.py
│   ├── models/
│   └── services/
├── docker/
│   └── docker-compose.yml
├── pipelines/
│   └── vanna_fastapi_pipeline.py
├── training/
│   ├── dataset.csv
│   └── training.ipynb
├── database/
├── static/
└── requirements.txt
```

## Quick Start

### Docker Deployment

```bash
# Clone repository
git clone <repository-url>
cd vanna-fastapi-backend

# Deploy all services
cd docker
docker-compose up -d

# Install Ollama model
docker exec ollama ollama pull qwen2.5:3b
```

**Services:**

- Ollama: http://localhost:11434
- Open WebUI: http://localhost:8000
- FastAPI Backend: http://localhost:4321

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run FastAPI server
python run.py
```

## Configuration

Environment variables in `.env`:

```bash
DEBUG=True

PORT=4321
APP_TITLE=Vanna SQL Assistant
APP_URL=http://localhost:4321

MODEL_NAME=qwen2.5:3b

STATIC_FOLDER=static
CHROMA_FOLDER=database
SQLITE_PATH=database.sqlite
```

## Training the Model

Use the `training.ipynb` notebook to train Vanna on your database:

1. Setup Vanna with Ollama and ChromaDB
2. Train on your database schema (DDL statements)
3. Train on question-SQL pairs from `training/dataset.csv`

The notebook handles the complete training process automatically.

## API Endpoints

The backend provides REST endpoints for SQL generation, query execution, visualization, and training data management. View full API documentation at `/docs` when running the server.

## Open WebUI Integration

The pipeline in `pipelines/vanna_fastapi_pipeline.py` connects Open WebUI to your FastAPI backend:

1. **Configure Pipeline**: Set API_URL to your FastAPI backend
2. **Deploy Pipeline**: Copy to Open WebUI pipelines folder
3. **Select Model**: Choose "Vanna Pipeline" in Open WebUI interface

**Pipeline Features:**

- Streams SQL generation process
- Formats results with local Ollama model
- Generates visualizations automatically
- Handles errors gracefully

## Usage Examples

### Through Open WebUI

1. Access http://localhost:8000
2. Setup the "Vanna Pipeline" model
3. Ask questions about your data in natural language

## Development

```bash
# Run in development mode
uvicorn app.main:app --reload --port 4321

# View API docs
# http://localhost:4321/docs
```

The FastAPI backend provides automatic OpenAPI documentation at `/docs` endpoint.
