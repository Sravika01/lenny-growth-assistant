import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import DOMPurify from "dompurify";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

type Source = {
  episode?: string;
  guest?: string;
  timestamp?: string;
  topic?: string;
  source_file?: string;
};

type Artifact = {
  id?: number;
  message_id?: number;
  artifact_type: "markdown" | "html";
  content: string;
  title?: string;
};

type Message = {
  id?: number;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

const quickPrompts = [
  {
    title: "Product Strategy",
    text: "What does Lenny say about product-market fit?",
    icon: "⌕",
    className: "prompt-blue",
  },
  {
    title: "Growth Lessons",
    text: "What are common growth lessons from Lenny's guests?",
    icon: "▥",
    className: "prompt-green",
  },
  {
    title: "Ship 30 for 30",
    text: "Write a Ship 30 for 30 essay about product discovery.",
    icon: "▤",
    className: "prompt-orange",
  },
  {
    title: "Create an Artifact",
    text: "Create an HTML landing page for a product idea.",
    icon: "</>",
    className: "prompt-purple",
  },
];

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [provider, setProvider] = useState("ollama");
  const [isLoading, setIsLoading] = useState(false);
  const [sources, setSources] = useState<Source[]>([]);
  const [artifact, setArtifact] = useState<Artifact | null>(null);

  useEffect(() => {
    createNewSession();
  }, []);

  async function createNewSession() {
    try {
      const response = await fetch(`${API_URL}/api/sessions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: "New Conversation",
        }),
      });

      if (!response.ok) {
        throw new Error("Unable to create session");
      }

      const data = await response.json();

      setSessionId(data.id);
      setMessages([]);
      setSources([]);
      setArtifact(null);
    } catch (error) {
      console.error(error);
    }
  }

  async function sendMessage(customMessage?: string) {
    const message = (customMessage ?? input).trim();

    if (!message || !sessionId || isLoading) {
      return;
    }

    setInput("");

    const userMessage: Message = {
      role: "user",
      content: message,
    };

    const assistantMessage: Message = {
      role: "assistant",
      content: "",
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
      assistantMessage,
    ]);

    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          message,
          provider,
        }),
      });

      if (!response.ok) {
        throw new Error("Unable to send message");
      }

      if (!response.body) {
        throw new Error("No response stream");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let accumulated = "";

      while (true) {
        const { value, done } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });

        const events = chunk.split("\n\n");

        for (const event of events) {
          if (!event.startsWith("data:")) {
            continue;
          }

          const rawData = event.replace(/^data:\s*/, "").trim();

          if (!rawData) {
            continue;
          }

          try {
            const data = JSON.parse(rawData);

            if (data.token) {
              accumulated += data.token;

              setMessages((previous) => {
                const updated = [...previous];

                updated[updated.length - 1] = {
                  role: "assistant",
                  content: accumulated,
                };

                return updated;
              });
            }

            if (data.sources) {
              setSources(data.sources);
            }

            if (data.artifacts && data.artifacts.length > 0) {
              setArtifact(data.artifacts[0]);
            }

            if (data.error) {
              throw new Error(data.error);
            }
          } catch (error) {
            console.error("Stream parsing error:", error);
          }
        }
      }
    } catch (error) {
      console.error(error);

      setMessages((previous) => {
        const updated = [...previous];

        updated[updated.length - 1] = {
          role: "assistant",
          content:
            "Sorry, I couldn't complete that request. Please try again.",
        };

        return updated;
      });
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    sendMessage();
  }

  function handlePrompt(text: string) {
    sendMessage(text);
  }

  function renderArtifact() {
    if (!artifact) {
      return (
        <div className="artifact-empty">
          <div className="artifact-empty-icon">
            <span>▤</span>
            <i>✦</i>
          </div>

          <h3>No artifact yet</h3>

          <p>
            When you ask for a Markdown or HTML artifact,
            <br />
            it will appear here.
          </p>
        </div>
      );
    }

    if (artifact.artifact_type === "html") {
      const safeHtml = DOMPurify.sanitize(artifact.content, {
        WHOLE_DOCUMENT: true,
      });

      return (
        <iframe
          title={artifact.title || "Generated artifact"}
          className="artifact-frame"
          sandbox="allow-scripts"
          srcDoc={safeHtml}
        />
      );
    }

    return (
      <div className="markdown-artifact">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {artifact.content}
        </ReactMarkdown>
      </div>
    );
  }

  return (
    <div className="app-shell">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span>✦</span>
        </div>

        <nav className="sidebar-nav">
          <button className="nav-item active">
            <span className="nav-icon">▣</span>
            <span>Chat</span>
          </button>

          <button className="nav-item">
            <span className="nav-icon">◷</span>
            <span>History</span>
          </button>

          <button className="nav-item">
            <span className="nav-icon">♧</span>
            <span>Prompts</span>
          </button>

          <button className="nav-item">
            <span className="nav-icon">⚙</span>
            <span>Settings</span>
          </button>
        </nav>

        <div className="sidebar-quote">
          <p>
            “Better
            <br />
            products.
            <br />
            Happier
            <br />
            users.”
          </p>

          <span>— Lenny Rachitsky</span>
        </div>
      </aside>

      {/* MAIN */}
      <div className="main-area">
        {/* HEADER */}
        <header className="topbar">
          <div className="brand">
            <div className="brand-mark">
              <span>✦</span>
            </div>

            <div>
              <h1>
                Lenny <span>Growth Assistant</span>
              </h1>

              <p>Ask. Learn. Build. Powered by Lenny's Podcast.</p>
            </div>
          </div>

          <div className="header-actions">
            <div className="provider-select">
              <span className="provider-icon">♙</span>

              <select
                value={provider}
                onChange={(event) => setProvider(event.target.value)}
              >
                <option value="ollama">Ollama · Local</option>
                <option value="anthropic">Anthropic · Cloud</option>
              </select>

              <span className="select-arrow">⌄</span>
            </div>

            <button
              className="new-chat-button"
              onClick={createNewSession}
            >
              <span>＋</span>
              New chat
            </button>
          </div>
        </header>

        {/* CONTENT */}
        <main className="content-area">
          {/* CHAT */}
          <section className="chat-panel">
            {messages.length === 0 ? (
              <div className="welcome-card">
                <div className="welcome-badge">
                  <span>✦</span>
                  Welcome to
                </div>

                <h2>
                  Lenny <span>Growth Assistant</span>
                </h2>

                <p className="welcome-description">
                  Ask product and growth questions from the podcast archive.
                  <br />
                  Get grounded answers, explore ideas, and generate content.
                </p>

                <div className="prompt-grid">
                  {quickPrompts.map((prompt) => (
                    <button
                      key={prompt.title}
                      className={`prompt-card ${prompt.className}`}
                      onClick={() => handlePrompt(prompt.text)}
                    >
                      <div className="prompt-icon">{prompt.icon}</div>

                      <strong>{prompt.title}</strong>

                      <span>“{prompt.text}”</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="messages-container">
                {messages.map((message, index) => (
                  <div
                    key={message.id ?? index}
                    className={`message-row ${
                      message.role === "user"
                        ? "user-row"
                        : "assistant-row"
                    }`}
                  >
                    {message.role === "assistant" && (
                      <div className="assistant-avatar">✦</div>
                    )}

                    <div
                      className={`message-bubble ${
                        message.role === "user"
                          ? "user-bubble"
                          : "assistant-bubble"
                      }`}
                    >
                      {message.role === "assistant" ? (
                        <>
                          {message.content ? (
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {message.content}
                            </ReactMarkdown>
                          ) : (
                            <div className="thinking">
                              <span></span>
                              <span></span>
                              <span></span>
                            </div>
                          )}
                        </>
                      ) : (
                        message.content
                      )}
                    </div>
                  </div>
                ))}

                {sources.length > 0 && (
                  <div className="sources-box">
                    <div className="sources-title">
                      Sources from Lenny's Podcast
                    </div>

                    {sources.slice(0, 5).map((source, index) => (
                      <div className="source-item" key={index}>
                        <span className="source-dot"></span>

                        <div>
                          <strong>
                            {source.episode || "Podcast Episode"}
                          </strong>

                          <span>
                            {source.guest
                              ? ` · ${source.guest}`
                              : ""}

                            {source.timestamp
                              ? ` · ${source.timestamp}`
                              : source.topic
                              ? ` · ${source.topic}`
                              : ""}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* COMPOSER */}
            <div className="composer-area">
              <form
                className="composer"
                onSubmit={handleSubmit}
              >
                <textarea
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (
                      event.key === "Enter" &&
                      !event.shiftKey
                    ) {
                      event.preventDefault();
                      handleSubmit(event);
                    }
                  }}
                  placeholder="Ask a question about product, growth, startups, or leadership..."
                  disabled={isLoading}
                />

                <div className="composer-bottom">
                  <div className="composer-status">
                    <span className="green-dot"></span>
                    Using{" "}
                    {provider === "ollama"
                      ? "local Ollama"
                      : "Anthropic Cloud"}
                  </div>

                  <button
                    type="submit"
                    className="send-button"
                    disabled={!input.trim() || isLoading}
                  >
                    <span>➤</span>
                    {isLoading ? "Thinking..." : "Send"}
                    <small>⌘ ↵</small>
                  </button>
                </div>
              </form>

              <div className="footer-note">
                Lenny Growth Assistant · v1.0.0
              </div>
            </div>
          </section>

          {/* ARTIFACT */}
          <section className="artifact-panel">
            <div className="artifact-header">
              <div className="artifact-title-wrapper">
                <div className="artifact-header-icon">▤</div>

                <div>
                  <h2>Artifact Viewer</h2>
                  <p>Generated content appears here.</p>
                </div>
              </div>
            </div>

            <div className="artifact-content">
              {renderArtifact()}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default App;