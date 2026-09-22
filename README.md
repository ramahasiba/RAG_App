# RAG App

A backend service for **Retrieval-Augmented Generation (RAG)**, built with FastAPI. It exposes an API for uploading documents, splitting them into chunks, embedding those chunks into a vector database, and answering natural-language questions grounded in the retrieved content — the classic *ingest → chunk → embed → index → retrieve → generate* pipeline.

The project is designed around swappable provider backends: LLM generation/embedding providers (OpenAI, Cohere) and a vector database provider (Qdrant) are all implemented behind common interfaces and created through factories, so new providers can be added without touching the rest of the app.

## Features

- 📁 **Project-based document management** — organize uploads into isolated projects
- 📄 **File ingestion** — upload `.txt` and `.pdf` files with type/size validation
- ✂️ **Chunking** — configurable recursive text splitting (via LangChain) with adjustable chunk size and overlap
- 🧠 **Pluggable LLM providers** — OpenAI and Cohere, used independently for generation and embeddings (e.g. generate with OpenAI, embed with Cohere)
- 🔎 **Vector search** — chunks are embedded and indexed in Qdrant for semantic similarity search
- 💬 **RAG question answering** — retrieves the most relevant chunks and generates a grounded answer
- 🌐 **Localized prompts** — English and Arabic prompt templates, selectable via config
- 🗄️ **MongoDB-backed metadata** — projects, assets, and chunks are persisted with async Motor/PyMongo

## Architecture

The codebase follows a loose MVC layout:

```
src/
├── main.py                 # FastAPI app, startup/shutdown lifecycle, router registration
├── routes/                 # API layer (views) — request/response schemas + endpoints
├── controllers/             # Business logic — validation, file handling, chunking, RAG orchestration
├── models/                  # Data layer — MongoDB models, Pydantic schemas, enums
├── stores/
│   ├── llm/                 # LLM provider interface, enums, factory, and OpenAI/Cohere implementations
│   ├── vectordb/            # Vector DB interface, enums, factory, and Qdrant implementation
│   └── templates/            # Prompt template parser + localized (en/ar) RAG prompt templates
└── helpers/
    └── config.py            # Pydantic Settings loaded from .env
```

**Provider pattern:** `LLMProviderFactory` and `VectorDBProviderFactory` read the configured backend name from settings and instantiate the matching provider class, each implementing a shared interface (`LLMInterface`, `VectorDBInterface`). This keeps generation, embedding, and vector storage decoupled from the rest of the application.

## Tech stack

| Layer | Technology |
|---|---|
| API framework | FastAPI + Uvicorn |
| App database | MongoDB (Motor / PyMongo) |
| Vector database | Qdrant (embedded/local mode) |
| LLM providers | OpenAI, Cohere |
| Document loading & chunking | LangChain (`PyMuPDFLoader`, `TextLoader`, `RecursiveCharacterTextSplitter`) |
| Config | Pydantic Settings (`.env`) |
| Containerization | Docker Compose (MongoDB) |

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Welcome / app info |
| `GET` | `/health` | Health check |
| `POST` | `/upload/{project_id}` | Upload a file to a project |
| `POST` | `/process/{project_id}` | Chunk an uploaded file and store chunks |
| `POST` | `/index/push/{project_id}` | Embed a project's chunks and index them in Qdrant |
| `GET` | `/index/info/{project_id}` | Get info about a project's vector collection |
| `POST` | `/index/search/{project_id}` | Semantic search over a project's indexed chunks |
| `POST` | `/index/answer/{project_id}` | Full RAG pipeline: retrieve relevant chunks and generate an answer |

## Getting started

### Prerequisites

- Python 3.10+
- Docker (for MongoDB)
- API keys for at least one LLM provider (OpenAI and/or Cohere)

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd RAG_App
pip install -r requirements.txt
```

> **Note:** `requirements.txt` currently only lists the core FastAPI stack. You'll also need to install `motor`, `pymongo`, `openai`, `cohere`, `qdrant-client`, `langchain-community`, `langchain-text-splitters`, and `pymupdf` — a `pip freeze > requirements.txt` after installing everything is recommended to keep it in sync.

### 2. Configure environment variables

Copy the example env file and fill in your values:

```bash
cp src/.env.example src/.env
```

In addition to the variables already listed in `.env.example`, the app also requires:

```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=rag_app
FILE_DEFAULT_CHUNK_SIZE=512
```

### 3. Start MongoDB

```bash
docker compose -f docker/docker-compose.yml up -d
```

Qdrant runs embedded (on-disk, at the path set by `VECTOR_DB_PATH`), so no separate service is needed for it.

### 4. Run the API

```bash
cd src
uvicorn main:app --host 0.0.0.0 --port 8060 --reload
```

The API will be available at `http://localhost:8060`, with interactive docs at `http://localhost:8060/docs`.

### Typical workflow

1. `POST /upload/{project_id}` — upload a document
2. `POST /process/{project_id}` — chunk it
3. `POST /index/push/{project_id}` — embed and index the chunks
4. `POST /index/answer/{project_id}` — ask a question grounded in the document

## Known limitations

- `requirements.txt` doesn't yet reflect all runtime dependencies (see note above)
- Qdrant runs in embedded/local mode only — no networked/clustered vector DB support yet
- `PINECONE_API_KEY` and `GROQ_API_KEY` exist as config placeholders but aren't wired to any provider
- No automated test suite yet
- No Dockerfile for the app itself (only MongoDB is containerized)

## License

No license has been specified for this project yet.
