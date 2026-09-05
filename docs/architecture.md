# Architecture — The Lenny Growth Assistant

## 1. Overview

The Lenny Growth Assistant is a full-stack conversational AI application that answers product and growth questions using Lenny's Podcast transcripts.

The system has four main layers:

1. React frontend
2. FastAPI backend
3. Agent + RAG layer
4. PostgreSQL + pgvector knowledge store

The application supports both:

- Local Ollama inference
- Cloud Anthropic inference

The provider is selected through configuration and the application UI.

---

## 2. High-Level Architecture

```text
                    ┌─────────────────────────┐
                    │       React + Vite      │
                    │                         │
                    │  Chat UI                │
                    │  Provider Selector      │
                    │  Source Display         │
                    │  Artifact Viewer         │
                    └────────────┬────────────┘
                                 │
                                 │ HTTP / SSE
                                 ▼
                    ┌─────────────────────────┐
                    │       FastAPI API       │
                    │                         │
                    │  Sessions               │
                    │  Chat                   │
                    │  Streaming              │
                    │  Health                 │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     Agent Layer         │
                    │                         │
                    │ LangChain create_agent  │
                    │ Transcript Search Tool  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       RAG Layer         │
                    │                         │
                    │ Query Embedding         │
                    │ pgvector Similarity     │
                    │ Top-K Retrieval         │
                    │ Source Metadata         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ PostgreSQL + pgvector   │
                    │                         │
                    │ Sessions                │
                    │ Messages                │
                    │ Transcript Chunks       │
                    │ Artifacts               │
                    └─────────────────────────┘

                         LLM Providers
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
        ┌─────────────────┐       ┌─────────────────┐
        │ Ollama          │       │ Anthropic       │
        │ Local model     │       │ Cloud model     │
        └─────────────────┘       └─────────────────┘

3. Frontend Architecture

The frontend is implemented using React, TypeScript, and Vite.

Responsibilities

The frontend handles:

Conversation interface
Session creation
Provider selection
User messages
Assistant responses
Streaming response display
Transcript source display
Markdown rendering
Artifact rendering
Responsive two-column layout
Main components
frontend/src/
├── App.tsx
├── components/
├── hooks/
└── lib/

The frontend communicates with the backend through HTTP APIs.

Streaming responses use Server-Sent Events (SSE).

4. Backend Architecture

The backend uses FastAPI.

backend/app/
├── main.py
├── config.py
├── database.py
├── agent.py
├── agent_framework.py
├── models/
├── providers/
├── rag/
├── skills/
└── api/
API responsibilities

The backend is responsible for:

Request validation
Session management
Conversation persistence
Agent execution
Transcript retrieval
LLM provider selection
Artifact persistence
Health checks
Structured error responses
5. Agent Architecture

The application uses a tool-based agent architecture.

The agent has access to a transcript search tool:

User Question
     │
     ▼
Lenny Growth Agent
     │
     ▼
search_lenny_transcripts()
     │
     ▼
Vector Retrieval
     │
     ▼
Relevant Transcript Chunks
     │
     ▼
Agent generates grounded answer

The agent is instructed to:

Search the transcript archive before answering factual questions.
Use only retrieved transcript information.
Avoid inventing facts.
Cite transcript-supported claims.
Admit when the archive does not contain sufficient information.
Use previous conversation context for follow-up questions.
6. Retrieval-Augmented Generation

The RAG pipeline uses sentence-transformer embeddings and PostgreSQL pgvector.

Retrieval process
User Question
      │
      ▼
Embedding Model
      │
      ▼
384-dimensional vector
      │
      ▼
pgvector cosine similarity
      │
      ▼
Top 5 transcript chunks
      │
      ▼
Similarity threshold
      │
      ▼
Agent context
Embedding model
all-MiniLM-L6-v2

The model generates 384-dimensional embeddings.

Retrieval configuration
TOP_K = 5
MIN_SIMILARITY = 0.25

Only transcript chunks above the minimum similarity threshold are returned.

7. Transcript Knowledge Base

Transcript files are stored under:

data/transcripts/

The ingestion pipeline:

Reads Markdown transcript files.
Excludes README files.
Extracts basic episode/source metadata.
Splits transcripts into overlapping chunks.
Generates embeddings.
Stores chunks and embeddings in PostgreSQL.

The current chunking strategy uses approximately:

Chunk size: 700 words
Overlap: 100 words

The ingestion script can be rerun to refresh the knowledge base.

8. Source Traceability

Every retrieved transcript chunk contains source metadata.

The metadata includes:

episode
guest
timestamp
topic
source_file

The agent is instructed to cite claims using:

[Episode: Guest Name, Timestamp/Topic]

This allows users to understand which transcript content supports an answer.

9. LLM Provider Layer

The application separates the LLM implementation from the rest of the application.

LLMProvider
     │
     ├── OllamaProvider
     │
     └── CloudProvider

Both providers expose:

generate()
stream()

This allows the application to switch providers without changing the application logic.

Ollama

Ollama runs locally and is the mandatory demo provider.

Default configuration:

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
Anthropic

Anthropic provides optional cloud inference.

The API key is supplied through environment configuration and is never committed to Git.

10. Conversation Persistence

PostgreSQL stores conversation state.

Sessions

A session contains:

id
title
created_at
updated_at
Messages

Each message contains:

id
session_id
role
content
sources
created_at

This provides independent conversation sessions and persistent message history.

11. Artifact Architecture

The assistant can generate Markdown or HTML artifacts from the current conversation.

The flow is:

User Request
     │
     ▼
Artifact Generation
     │
     ▼
Markdown / HTML
     │
     ▼
Artifact Persistence
     │
     ▼
Artifact Viewer

Artifacts are stored separately from normal messages.

Artifact fields
id
message_id
artifact_type
content

Supported artifact types:

markdown
html
12. Artifact Security

Generated HTML is treated as untrusted content.

The frontend uses:

DOMPurify where applicable
Sandboxed iframe rendering
sandbox="allow-scripts"

The iframe intentionally does not use:

allow-same-origin

This limits the ability of generated content to access the application's origin.

Generated HTML is therefore isolated from the main application interface.

13. Ship 30 for 30 Skill

Ship 30 for 30 is implemented as a dedicated generation path.

When a user requests a Ship 30 / 30-for-30 style essay, the system:

Retrieves relevant transcript context.
Builds a specialized Ship 30 prompt.
Generates the content using the selected provider.
Returns transcript-grounded claims and sources.

The generated piece is expected to contain:

Strong hook
Clear narrative
Skimmable structure
Headings
Bullets where useful
Bold emphasis where useful
Practical takeaway
Transcript-grounded claims
14. API Endpoints
Create session
POST /api/sessions

Creates an independent conversation session.

Get session
GET /api/sessions/{session_id}

Returns session information.

Chat
POST /api/chat

Processes a user message and returns the completed assistant response.

Streaming chat
POST /api/chat/stream

Returns the assistant response through Server-Sent Events.

Health
GET /api/health

Checks:

Database connectivity
Ollama availability

Example:

{
  "status": "ok",
  "database": "ok",
  "ollama": "ok"
}
15. Error Handling

The API uses structured error categories.

Examples include:

session_not_found
database_error
model_unavailable
agent_error

Provider-specific failures are converted into user-safe error messages.

Examples:

Ollama unavailable
Model timeout
Invalid provider
Missing Anthropic API key
Database failure

Sensitive configuration values are not returned to users.

16. Docker Architecture

The project uses Docker Compose.

docker-compose.yml

     ┌─────────────────┐
     │    Frontend     │
     │     :5173       │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │    Backend      │
     │     :8000       │
     └───────┬─────────┘
             │
       ┌─────┴─────┐
       ▼           ▼
┌────────────┐ ┌────────────┐
│ PostgreSQL │ │   Ollama   │
│ pgvector   │ │   Local    │
└────────────┘ └────────────┘

The PostgreSQL container uses the pgvector image.

The backend connects to PostgreSQL through the Docker network.

The backend connects to Ollama running on the host through:

host.docker.internal:11434
17. Configuration

Configuration is environment-driven.

The project provides:

.env.example

Important settings include:

DATABASE_URL
DEFAULT_LLM_PROVIDER
OLLAMA_BASE_URL
OLLAMA_MODEL
ANTHROPIC_API_KEY
ANTHROPIC_MODEL

Secrets are excluded from version control using .gitignore.

18. Operational Health

The health endpoint provides a basic readiness signal for the main dependencies.

The system checks:

Application
    │
    ├── PostgreSQL
    │
    └── Ollama

Docker Compose also uses a PostgreSQL health check before starting the backend dependency.

19. Key Design Decisions
PostgreSQL + pgvector

Chosen because the application requires persistent relational data together with vector similarity search.

Local Ollama

Chosen because local inference is mandatory for the demo and allows the application to run without a cloud API key.

Provider abstraction

Chosen to prevent provider-specific logic from spreading across the application.

Tool-based agent

Chosen so the agent explicitly calls transcript retrieval before answering factual questions.

Sandboxed artifacts

Chosen because generated HTML is untrusted and must not execute with the application's normal origin privileges.

SSE

Chosen for simple HTTP-compatible streaming between the FastAPI backend and browser frontend.

20. Main Data Flow

A normal question follows this path:

User
 │
 ▼
React UI
 │
 ▼
POST /api/chat/stream
 │
 ▼
FastAPI
 │
 ▼
Conversation History
 │
 ▼
LangChain Agent
 │
 ▼
Transcript Search Tool
 │
 ▼
Query Embedding
 │
 ▼
pgvector
 │
 ▼
Top Relevant Chunks
 │
 ▼
Grounded Agent Prompt
 │
 ▼
Ollama / Anthropic
 │
 ▼
Assistant Response
 │
 ├── Citations
 │
 └── Sources
 │
 ▼
PostgreSQL
 │
 ▼
React UI
21. Refreshing the Knowledge Base

The transcript knowledge base can be refreshed by rerunning the ingestion process.

The ingestion process replaces existing transcript chunks with the current transcript dataset.

This keeps the vector store synchronized with the downloaded transcript archive.

22. Deployment Model

The local deployment consists of:

Docker Compose
├── PostgreSQL + pgvector
├── FastAPI backend
└── React frontend

Host
└── Ollama

This architecture keeps infrastructure reproducible while allowing Ollama to use the local machine's resources.

23. Known Trade-offs
Word-based chunking

The current implementation uses word-based chunking rather than an exact tokenizer-based token count.

This keeps ingestion simple while maintaining overlapping context.

Local model size

The default Ollama model is relatively small so the application can run on typical developer hardware.

Larger models can improve answer quality at the cost of latency and resource usage.

SSE transport

SSE provides simple browser-compatible streaming but is unidirectional. The client sends requests through HTTP and receives streamed responses through the SSE response.

Retrieval threshold

A similarity threshold is used to reduce unsupported answers, but retrieval quality depends on the embedding model and transcript chunking strategy.

24. Security Principles

The application follows these principles:

Never commit API keys.
Treat generated HTML as untrusted.
Sandbox generated HTML.
Do not grant allow-same-origin to generated artifacts.
Validate API request bodies with Pydantic.
Return safe structured errors.
Ground factual answers in retrieved transcript content.
Explicitly admit when the transcript archive does not contain enough information.

