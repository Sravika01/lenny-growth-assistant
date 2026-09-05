# Product Requirements Document
# The Lenny Growth Assistant

## 1. Product Overview

The Lenny Growth Assistant is a full-stack AI assistant that allows product and growth teams to ask questions grounded in Lenny's Podcast transcripts.

The product combines:

- Conversational question answering
- Transcript-based retrieval
- Source attribution
- Follow-up conversation context
- Ship 30 for 30 content generation
- Markdown and HTML artifact generation
- In-app artifact rendering
- Local Ollama inference
- Optional cloud LLM inference

The goal is to make the knowledge contained in Lenny's Podcast easier to search, understand, reuse, and turn into practical product/growth content.

---

# 2. Discovery Brief

## 2.1 User

The primary user is a product, growth, startup, or product-management professional who wants to learn from the ideas discussed across Lenny's Podcast.

The user should not need to understand:

- Prompt engineering
- RAG pipelines
- Embeddings
- Vector databases
- LLM providers
- AI infrastructure

They should be able to ask a question naturally and receive a useful, source-grounded answer.

---

## 2.2 User Problem

Lenny's Podcast contains a large amount of product and growth knowledge spread across many episodes and transcripts.

Manually finding relevant discussions requires:

1. Knowing which episode contains the answer
2. Searching through transcripts
3. Reading potentially long transcripts
4. Comparing ideas across episodes
5. Turning the information into reusable content

The assistant removes this manual search and synthesis burden.

---

## 2.3 Primary Jobs To Be Done

### Job 1 — Find an answer

"When I have a product or growth question, I want to quickly find relevant ideas from Lenny's Podcast."

### Job 2 — Understand an idea

"When I find relevant transcript material, I want the assistant to explain it clearly."

### Job 3 — Continue the conversation

"When I ask a follow-up question, I want the assistant to understand the previous context."

### Job 4 — Reuse knowledge

"When I discover a useful idea, I want to turn it into a polished written artifact."

---

# 3. Success Metrics

## Product Metrics

### Grounding / citation accuracy

Target:

**≥ 90% of factual answers should contain transcript-supported citations.**

### Out-of-domain behavior

When the transcript archive does not contain sufficient information, the assistant should explicitly acknowledge the limitation rather than inventing an answer.

### Session continuity

Follow-up questions should preserve the current session's conversational context.

---

## Operational Metrics

### Local inference

Target:

**< 4 seconds to first token where practical on the demo machine.**

Actual latency may vary depending on hardware and model size.

### Artifact security

Generated HTML must be treated as untrusted content.

Target:

**0 known XSS paths through the artifact viewer.**

The viewer uses sanitization and a sandboxed iframe without `allow-same-origin`.

---

# 4. Assumptions

The following assumptions were made because the brief does not specify them explicitly.

1. The primary user is an internal product/growth professional rather than a public consumer.
2. Transcript knowledge is more important than general web knowledge.
3. The assistant should prioritize correctness and source traceability over speculative answers.
4. Ollama is the default local provider for evaluation.
5. PostgreSQL with pgvector is sufficient for the initial transcript corpus.
6. Five retrieved transcript chunks are sufficient as the initial retrieval context.
7. A single-user local deployment is sufficient for the assignment demonstration.
8. Authentication is outside the initial assignment scope.
9. Generated HTML is untrusted and must never receive unrestricted browser privileges.
10. The transcript repository can be refreshed through the ingestion process when source data changes.

---

# 5. Scope

## Included

### Conversational assistant

- New sessions
- Independent session context
- Follow-up questions
- Streaming responses
- Transcript-grounded answers

### Knowledge base

- Lenny's Podcast transcripts
- Chunking
- Embeddings
- PostgreSQL
- pgvector similarity search
- Source metadata

### Model layer

- Ollama
- Local LLM
- Anthropic cloud provider
- Provider configuration

### Content generation

- Ship 30 for 30 writing skill
- Approximately 1,250-word essays
- Markdown artifacts
- HTML artifacts

### Artifact viewer

- Side-by-side artifact panel
- Markdown rendering
- HTML rendering
- Sanitization
- Sandboxed iframe

### Operations

- Docker Compose
- Environment configuration
- Health checks
- Error handling
- Automated tests

---

# 6. Intentionally Excluded

The following are intentionally outside the initial scope:

### Authentication and authorization

The assignment does not require user accounts or enterprise identity management.

### Multi-tenant architecture

The demonstration is designed around independent application sessions rather than a multi-tenant SaaS architecture.

### Real-time transcript synchronization

The system supports explicit ingestion/refresh rather than continuously monitoring the upstream repository.

### External web search

The assistant is intentionally restricted to the Lenny transcript knowledge base for factual podcast-related answers.

### Advanced analytics

Usage dashboards, user analytics, and business intelligence are not required for the initial product.

### Production cloud deployment

The assignment prioritizes a reproducible local deployment with Docker Compose.

---

# 7. Core User Flow

```text
User opens application
        ↓
New conversation/session created
        ↓
User asks product/growth question
        ↓
LangChain agent receives question
        ↓
Transcript retrieval tool searches pgvector
        ↓
Relevant transcript chunks returned
        ↓
LLM generates grounded answer
        ↓
Sources displayed with answer
        ↓
User asks follow-up
        ↓
Previous session context is included

---

# 8. Ship 30 for 30 Flow
User requests Ship 30 essay
        ↓
Relevant transcript chunks retrieved
        ↓
Ship 30 writing skill constructs grounded prompt
        ↓
LLM generates approximately 1,250-word essay
        ↓
Markdown content returned
        ↓
Artifact Viewer renders the document
9. Artifact Flow
User requests HTML/Markdown
        ↓
Transcript context retrieved
        ↓
LLM generates artifact
        ↓
Artifact extracted from response
        ↓
Artifact persisted with assistant message
        ↓
Frontend receives artifact
        ↓
Markdown → ReactMarkdown
HTML → DOMPurify → sandboxed iframe
10. Acceptance Criteria
Conversational assistant
 User can create a new conversation.
 Conversations have unique session IDs.
 Messages are persisted.
 Assistant can answer transcript-grounded questions.
 Sources are returned with answers.
 Follow-up questions preserve session context.
 Assistant can state when the archive does not contain enough information.
Knowledge base
 Transcript files can be ingested.
 Transcript content is chunked.
 Embeddings are generated.
 Embeddings are stored in pgvector.
 Source file information is preserved.
 README content is excluded from transcript ingestion.
LLM
 Ollama is supported.
 Cloud provider is supported.
 Provider is configurable.
 Missing cloud credentials produce an explicit error.
Ship 30
 Dedicated Ship 30 writing skill exists.
 Output targets approximately 1,250 words.
 Output is Markdown.
 Claims must be grounded in transcript context.
Artifacts
 Markdown artifacts can be rendered.
 HTML artifacts can be rendered.
 HTML is sanitized.
 HTML is rendered in a sandboxed iframe.
 allow-same-origin is not granted.
Operations
 Docker Compose configuration exists.
 Backend container exists.
 Frontend container exists.
 PostgreSQL container exists.
 Health endpoint checks database and Ollama.
 Automated tests exist.
11. Risks and Trade-offs
Hallucination
Risk

An LLM may generate information that is not present in the transcripts.

Decision

The agent is instructed to search the transcript tool before answering factual podcast questions and to refuse unsupported answers.

Retrieval quality
Risk

Semantic retrieval can return related but insufficient chunks.

Decision

Use embedding-based retrieval with a similarity threshold and top-5 results.

This is simple enough for the assignment while remaining extensible.

Local model quality
Risk

A small local model may produce lower-quality responses than a larger cloud model.

Decision

Ollama is the default demo provider because local inference is mandatory for evaluation. A cloud provider is also supported for higher-quality inference.

Latency
Risk

Local embedding generation and LLM inference can be slower than cloud inference.

Decision

Embeddings are generated during ingestion rather than during every query. Retrieval only generates an embedding for the user's query.

Cost
Risk

Cloud inference introduces API costs.

Decision

Ollama is available as a no-API-cost local provider.

Data leakage
Risk

Sensitive data could be sent to an external model provider.

Decision

The system can run entirely with local Ollama inference. Cloud inference is optional.

Unsafe artifact rendering
Risk

Generated HTML may contain malicious JavaScript or unsafe browser behavior.

Decision

Generated HTML is sanitized using DOMPurify and rendered in an iframe using:

sandbox="allow-scripts"

without:

allow-same-origin

This limits the artifact's privileges and separates it from the main application origin.

12. Implementation Plan
Phase 1 — Foundation
FastAPI
PostgreSQL
pgvector
React frontend
Docker Compose
Phase 2 — Knowledge
Transcript ingestion
Chunking
Embeddings
Retrieval
Source attribution
Phase 3 — Agent
LangChain agent
Transcript search tool
Ollama integration
Cloud provider integration
Phase 4 — Product Features
Conversational sessions
Streaming
Ship 30 skill
Artifact generation
Artifact viewer
Phase 5 — Production Readiness
Health checks
Error handling
Tests
Docker validation
Documentation
Phase 6 — Handoff
README
Architecture documentation
Design documentation
Agent transcripts
GitHub repository
Demo video
13. Definition of Done

The project is considered ready for evaluator handoff when:

The application starts reproducibly.
The evaluator can run the local Ollama demo.
Questions return transcript-grounded answers.
Sources are visible.
Follow-up questions work.
Ship 30 generation works.
HTML/Markdown artifacts render inside the application.
Generated HTML is isolated from the application.
PostgreSQL persistence works.
Health checks expose service status.
Automated tests pass.
Documentation explains how to run and extend the system.
No secrets are committed.
The GitHub repository contains the complete submission.
A 2–3 minute demo demonstrates the core experience.