# The Lenny Growth Assistant

A full-stack AI conversational assistant that answers product, growth, startup, and leadership questions using Lenny's Podcast transcripts.

The application provides:

- Transcript-grounded conversational answers
- RAG with PostgreSQL + pgvector
- LangChain agent with transcript search tool
- Local Ollama inference
- Optional Anthropic cloud inference
- Conversation/session persistence
- Source citations
- Ship 30 for 30 writing
- Markdown and HTML artifact generation
- Sandboxed artifact preview
- Docker Compose deployment
- Health checks and structured API errors

---

## 1. Tech Stack

### Frontend

- React
- TypeScript
- Vite
- React Markdown
- DOMPurify

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- LangChain

### Database

- PostgreSQL
- pgvector

### AI

- Ollama
- llama3.2:3b
- Anthropic API (optional)

### Embeddings

- sentence-transformers
- all-MiniLM-L6-v2

### Infrastructure

- Docker
- Docker Compose

---

## 2. Project Structure

```text
lenny-growth-assistant/
├── .env.example
├── docker-compose.yml
├── README.md
├── docs/
│   ├── PRD.md
│   ├── architecture.md
│   └── design.md
├── agent_transcripts/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── scripts/
│   ├── app/
│   └── tests/
├── data/
│   └── transcripts/
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── src/

3. Prerequisites

Install:

Python 3.11+
Node.js
Docker Desktop
Ollama

The application is designed to support local Ollama inference for the demo.

4. Environment Configuration

Copy the example environment file:

cp .env.example .env

The default configuration uses Ollama:

DEFAULT_LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

Anthropic is optional.

If using Anthropic, configure:

ANTHROPIC_API_KEY=your_api_key

Never commit .env or API keys.

5. Install Ollama Model

Start Ollama and pull the model:

ollama pull llama3.2:3b

Verify Ollama:

ollama list
6. Start the Application

From the project root:

docker compose up -d

Check running services:

docker compose ps

The application services are:

Frontend:  http://localhost:5173
Backend:   http://localhost:8000
Database:  localhost:5433
Ollama:    localhost:11434

Open:

http://localhost:5173
7. Health Check

Run:

curl http://localhost:8000/api/health

A healthy environment returns:

{
  "status": "ok",
  "database": "ok",
  "ollama": "ok"
}
8. Transcript Knowledge Base

The application uses transcripts from Lenny's Podcast transcript repository.

Transcript files are stored under:

data/transcripts/

The ingestion pipeline:

Reads transcript Markdown files.
Excludes README files.
Extracts source metadata.
Splits transcripts into overlapping chunks.
Generates embeddings.
Stores embeddings in PostgreSQL using pgvector.

Current chunking configuration:

Chunk size: approximately 700 words
Overlap: 100 words
9. Run Ingestion

Activate the backend environment if running locally:

cd backend
source .venv/bin/activate

Then run:

PYTHONPATH=. python scripts/ingest.py

The ingestion process refreshes the transcript vector store.

10. RAG Retrieval

The retrieval system uses:

Embedding model:
all-MiniLM-L6-v2

Vector dimensions:
384

Top K:
5

Minimum similarity:
0.25

The agent retrieves relevant transcript chunks before answering factual questions.

11. Grounding

The assistant is instructed to:

Use the transcript search tool.
Use only retrieved transcript information.
Avoid unsupported claims.
Cite transcript-supported claims.
Admit when the archive does not contain enough information.

Citation format:

[Episode: Guest Name, Timestamp/Topic]

When there is insufficient evidence, the assistant should respond:

I do not have sufficient information in Lenny's podcast archive to answer this.
12. LLM Providers

The application supports two providers.

Ollama

Default provider for local inference.

DEFAULT_LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b
Anthropic

Optional cloud provider.

DEFAULT_LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_api_key

Provider-specific logic is isolated behind a common provider interface.

13. Sessions and Persistence

Each conversation has an independent session ID.

PostgreSQL stores:

Sessions
Messages
Transcript chunks
Sources
Artifacts

This allows conversations to maintain context across follow-up questions.

14. Ship 30 for 30

The application includes a dedicated Ship 30 for 30 generation path.

The assistant uses retrieved podcast transcript context to create a structured essay containing:

Strong hook
Narrative
Skimmable headings
Bullets
Bold emphasis
Practical takeaway
Transcript-grounded claims
15. Artifact Generation

The assistant can generate:

Markdown
HTML

Generated artifacts appear inside the application's Artifact Viewer.

Users do not need to copy generated code into another application.

16. Artifact Security

Generated HTML is treated as untrusted content.

The frontend uses a sandboxed iframe:

sandbox="allow-scripts"

The sandbox intentionally does not grant:

allow-same-origin

DOMPurify is also used where applicable.

This prevents generated HTML from receiving the application's normal origin privileges.

17. API
Create session
POST /api/sessions
Get session
GET /api/sessions/{session_id}
Chat
POST /api/chat
Streaming chat
POST /api/chat/stream
Health
GET /api/health
18. Testing

Run backend tests:

cd backend
source .venv/bin/activate
pytest -v

The tests cover areas including:

API availability
Provider configuration
Retrieval configuration
19. Stopping the Application
docker compose down

To remove the PostgreSQL volume as well:

docker compose down -v

Warning: removing the volume deletes the local PostgreSQL data.

20. Troubleshooting
Ollama unavailable

Check:

ollama list

Make sure Ollama is running.

Backend unavailable

Check:

docker compose logs backend
Frontend unavailable

Check:

docker compose logs frontend
Database unavailable

Check:

docker compose logs db
Rebuild containers
docker compose up -d --build
21. Design Documentation

Additional project documentation:

docs/PRD.md — product requirements and success criteria
docs/architecture.md — technical architecture
docs/design.md — UX and product design
22. AI-Assisted Development

AI tools were used during development for:

Project scaffolding
Debugging
Code generation
Architecture iteration
Test creation
Documentation

All generated code was reviewed, tested, and modified during implementation.

Development notes and sanitized agent transcripts are included in:

agent_transcripts/
23. Definition of Done

The project is considered complete when:

 Full-stack application runs locally
 PostgreSQL + pgvector configured
 Transcript knowledge base ingested
 RAG retrieval implemented
 Agent-based transcript search implemented
 Ollama local inference works
 Anthropic provider supported
 Conversation persistence implemented
 Source attribution implemented
 Ship 30 for 30 generation implemented
 Artifact viewer implemented
 HTML artifacts sandboxed
 Docker Compose configured
 Health endpoint implemented
 Tests included
 Product and architecture documentation included