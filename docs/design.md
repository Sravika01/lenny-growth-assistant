# Product & UX Design — The Lenny Growth Assistant

## 1. Design Goal

The Lenny Growth Assistant is designed to make it easy for users to ask product, growth, startup, and leadership questions and receive answers grounded in Lenny's Podcast transcripts.

The interface prioritizes:

- Simple conversation
- Clear source attribution
- Fast feedback
- Provider visibility
- Easy artifact generation
- Safe artifact rendering

---

## 2. Target User

The primary user is a product, growth, startup, or business professional who wants to learn from ideas discussed on Lenny's Podcast.

Typical tasks include:

- Asking product strategy questions
- Asking growth questions
- Exploring ideas discussed by podcast guests
- Asking follow-up questions
- Creating a Ship 30 for 30 style essay
- Generating a Markdown or HTML artifact

---

## 3. Main User Flow

```text
Open Application
       ↓
Create / Select Conversation
       ↓
Select LLM Provider
       ↓
Ask Question
       ↓
Assistant Searches Transcript Knowledge Base
       ↓
Grounded Answer + Sources
       ↓
Ask Follow-up
       ↓
Continue Conversation

4. Layout

The application uses a responsive two-column layout.

┌─────────────────────────────────────────────────────────────┐
│                 Lenny Growth Assistant                      │
├─────────────────────────────┬───────────────────────────────┤
│                             │                               │
│       CHAT                  │       ARTIFACT                │
│                             │                               │
│  User message               │  Preview                      │
│                             │                               │
│  Assistant response         │  Markdown / HTML              │
│                             │                               │
│  Sources                    │                               │
│                             │                               │
│  ┌───────────────────────┐  │                               │
│  │ Ask a question...     │  │                               │
│  └───────────────────────┘  │                               │
└─────────────────────────────┴───────────────────────────────┘
5. Chat Experience

The chat interface provides:

User messages
Assistant messages
Loading/streaming feedback
Source references
Quick prompts
Conversation continuity

The assistant response is displayed as readable Markdown rather than raw generated text.

6. Source Display

Transcript sources are displayed with the assistant response.

A source contains information such as:

Episode
Guest
Timestamp or topic
Source file

Example:

Sources

Episode: Example Episode
Guest: Example Guest
Topic: Product Strategy

The goal is to make the answer traceable to the podcast archive.

7. Provider Selection

The interface provides a visible provider selector.

Supported providers:

Ollama
Anthropic

Ollama is the default provider because local inference is required for the demo.

The provider selection is passed to the backend so the user can change the model provider without changing application code.

8. Quick Prompts

The interface provides example prompts to help users understand what the assistant can do.

Examples:

What are common product growth lessons from Lenny's Podcast?

What advice have guests given about finding product-market fit?

Help me understand how successful teams prioritize product ideas.

Write a Ship 30 for 30 essay about product discovery.

These prompts are shortcuts and do not restrict the user from asking arbitrary questions.

9. Follow-up Questions

Conversation context is maintained using the session ID.

Example:

User:
What does Lenny say about product-market fit?

Assistant:
[Grounded answer]

User:
What about measuring it?

Assistant:
Uses the previous conversation context together with
new transcript retrieval.

This allows natural multi-turn conversations.

10. Empty / Unsupported Questions

If the transcript archive does not contain enough relevant information, the assistant should not guess.

The application displays:

I do not have sufficient information in Lenny's podcast archive to answer this.

This is preferable to producing an apparently confident but unsupported answer.

11. Artifact Viewer

The artifact viewer appears beside the conversation.

Supported artifact types:

Markdown
HTML
Markdown

Markdown is rendered directly in the application.

HTML

HTML is rendered inside an isolated sandboxed iframe.

The artifact viewer is designed to make generated content immediately useful without requiring the user to copy code into another application.

12. Artifact Security

Generated HTML is considered untrusted.

The rendering strategy uses:

DOMPurify
+
sandboxed iframe
+
sandbox="allow-scripts"

The iframe does not receive:

allow-same-origin

This prevents generated content from receiving the application's normal origin privileges.

The generated artifact therefore remains isolated from the main application.

13. Ship 30 for 30 Experience

When a user asks for a Ship 30 for 30 essay, the assistant follows a dedicated generation path.

The generated content should have:

Strong opening hook
Clear narrative
Short paragraphs
Headings
Bullets where appropriate
Bold emphasis where useful
Practical takeaway
Claims grounded in transcript sources

The experience should feel like a writing assistant rather than a generic chatbot response.

14. Loading and Error States

The UI provides feedback for important states.

Loading
Assistant is thinking...
Ollama unavailable
Ollama is unavailable. Please make sure Ollama is running.
Timeout
Ollama request timed out. Please try again.
Invalid provider
The selected model provider is not available.
Database/API failure
The assistant could not complete the request.
Please try again.

Errors should be understandable to users without exposing internal stack traces.

15. Visual Design Principles

The interface follows these principles:

Clarity

The user should immediately understand:

Where to ask a question
Which model provider is active
Where the answer appears
Which sources support the answer
Where generated artifacts appear
Minimalism

Only functionality required by the assignment is exposed.

Readability

Long AI responses should remain easy to scan using:

Headings
Paragraph spacing
Lists
Bold emphasis
Code formatting where required
Responsive Design

The application should remain usable on desktop and smaller screens.

16. Accessibility

The UI should provide:

Semantic buttons
Visible focus states
Readable contrast
Keyboard-accessible controls
Descriptive labels
Appropriate heading hierarchy

The chat input should remain accessible while responses are being generated.

17. Performance Goals

The main performance goals are:

Fast initial UI load
Responsive chat input
Streaming feedback where supported
Efficient vector retrieval
Local inference suitable for the available hardware

The target from the product requirements is:

Local inference first-token latency: < 4 seconds

Actual performance depends on the selected Ollama model and local hardware.

18. Safety Goals

The application should:

Never expose API keys in the frontend
Never commit secrets
Avoid unsupported transcript claims
Clearly communicate insufficient retrieval
Treat generated HTML as untrusted
Isolate generated HTML from the main application
19. Design Trade-offs
Two-column interface

Provides simultaneous access to conversation and artifacts, but requires more horizontal space.

Local Ollama

Provides privacy and removes cloud dependency for the demo, but can have higher latency on limited hardware.

Source citations

Improve trust and traceability, but can make responses visually denser.

Sandboxed HTML

Improves security, but some advanced browser functionality may not work inside the sandbox.

20. Success Criteria

The design is successful when a user can:

Start a conversation quickly.
Ask a product or growth question.
Receive a transcript-grounded answer.
See supporting sources.
Ask a contextual follow-up.
Switch between supported model providers.
Generate a Ship 30 for 30 essay.
Generate a Markdown or HTML artifact.
Preview the artifact directly inside the application.
Use the application without interacting with raw generated code.