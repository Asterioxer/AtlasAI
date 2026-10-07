"use client";

import { DragEvent, FormEvent, useEffect, useState } from "react";

type Workspace = { id: string; name: string };
type Source = { id: string; name: string; source_type: string };
type Conversation = { id: string; workspace_id: string; title?: string | null };
type Message = { id: string; role: string; content: string };
type Citation = { chunk_id: string; source_id: string; document_id: string; score: number };

const API =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" && window.location.hostname !== "localhost"
    ? "https://atlasai-w5i8.onrender.com"
    : "http://localhost:8000");
const TOKEN = process.env.NEXT_PUBLIC_ATLAS_TOKEN || "demo-user";

const SUPPORTED_EXTENSIONS =
  ".pdf,.txt,.md,.markdown,.rst,.log,.csv,.tsv,.json,.yaml,.yml,.toml,.ini,.cfg,.conf,.xml,.html,.htm,.css,.js,.jsx,.ts,.tsx,.py,.java,.kt,.go,.rs,.c,.h,.cpp,.hpp,.cs,.php,.rb,.swift,.scala,.sql,.sh,.bash,.zsh,.ps1,.bat,.tex,.dockerfile,.rtf,.eml,.docx,.xlsx,.xls,.pptx,.odt,.ods,.odp,.epub";

const SUPPORTED_SUFFIXES = new Set([
  "pdf", "txt", "md", "markdown", "rst", "log", "csv", "tsv", "json", "yaml", "yml",
  "toml", "ini", "cfg", "conf", "xml", "html", "htm", "css", "js", "jsx", "ts", "tsx",
  "py", "java", "kt", "go", "rs", "c", "h", "cpp", "hpp", "cs", "php", "rb", "swift",
  "scala", "sql", "sh", "bash", "zsh", "ps1", "bat", "tex", "dockerfile", "rtf", "eml",
  "docx", "xlsx", "xls", "pptx", "odt", "ods", "odp", "epub",
]);

function getExtension(name: string) {
  const lower = name.toLowerCase();
  if (lower === "dockerfile" || lower.endsWith(".dockerfile")) return "dockerfile";
  const dot = lower.lastIndexOf(".");
  return dot >= 0 ? lower.slice(dot + 1) : "";
}

async function api(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${TOKEN}`);
  if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");

  let response: Response;
  try {
    response = await fetch(`${API}${path}`, { ...init, headers });
  } catch {
    throw new Error(`Cannot reach AtlasAI API at ${API}. Check the Render service and CORS configuration.`);
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
  return data;
}

function localTitle(conversation: Conversation, messages: Message[]) {
  if (conversation.title?.trim()) return conversation.title.trim();
  const firstUser = messages.find((message) => message.role === "user");
  if (firstUser?.content) return firstUser.content.slice(0, 34) + (firstUser.content.length > 34 ? "…" : "");
  return "New thread";
}

export default function ChatWorkspace() {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [lastUpload, setLastUpload] = useState<{ title: string; chunks: number } | null>(null);
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [creatingConversation, setCreatingConversation] = useState(false);
  const [booting, setBooting] = useState(true);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const currentConversation = conversations.find((conversation) => conversation.id === conversationId) ?? null;

  async function selectConversation(id: string) {
    setConversationId(id);
    setAnswer("");
    setCitations([]);
    setError("");
    setNotice("");

    try {
      const rows = await api(`/api/v1/conversations/${id}/messages`);
      setMessages(rows);

      const firstUser = rows.find((message: Message) => message.role === "user");
      if (firstUser) {
        setConversations((old) =>
          old.map((conversation) =>
            conversation.id === id && !conversation.title
              ? { ...conversation, title: firstUser.content.slice(0, 120) }
              : conversation
          )
        );
      }
    } catch (e) {
      setMessages([]);
      setError(e instanceof Error ? e.message : "Failed to load conversation");
    }
  }

  async function refresh(id: string, preferredConversationId?: string | null) {
    const [sourceRows, conversationRows] = await Promise.all([
      api(`/api/v1/workspaces/${id}/sources`),
      api(`/api/v1/workspaces/${id}/conversations`),
    ]);

    setSources(sourceRows);
    setConversations(conversationRows);

    const targetId = preferredConversationId ?? conversationId ?? conversationRows[0]?.id ?? null;
    if (targetId) {
      await selectConversation(targetId);
    } else {
      setConversationId(null);
      setMessages([]);
    }
  }

  async function initialize() {
    setBooting(true);
    setError("");
    try {
      const rows = await api("/api/v1/workspaces");
      const current: Workspace =
        rows[0] ??
        (await api("/api/v1/workspaces", {
          method: "POST",
          body: JSON.stringify({ name: "AtlasAI Demo" }),
        }));

      setWorkspace(current);
      await refresh(current.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to initialize workspace");
    } finally {
      setBooting(false);
    }
  }

  useEffect(() => {
    void initialize();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function newConversation() {
    if (!workspace || creatingConversation) return;

    setCreatingConversation(true);
    setError("");
    setNotice("");

    try {
      const row = await api(`/api/v1/workspaces/${workspace.id}/conversations`, { method: "POST" });
      setConversations((old) => [row, ...old]);
      setConversationId(row.id);
      setMessages([]);
      setAnswer("");
      setCitations([]);
      setQuestion("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not create conversation");
    } finally {
      setCreatingConversation(false);
    }
  }

  function chooseFile(nextFile: File | null) {
    if (!nextFile) return;

    const extension = getExtension(nextFile.name);
    if (!SUPPORTED_SUFFIXES.has(extension)) {
      setFile(null);
      setError(
        "Unsupported file type. AtlasAI accepts PDF, Office, spreadsheets, presentations, structured data, email, markup, source code, and ebook formats."
      );
      return;
    }

    setError("");
    setNotice("");
    setLastUpload(null);
    setFile(nextFile);
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragging(false);
    chooseFile(event.dataTransfer.files?.[0] ?? null);
  }

  async function upload() {
    if (!workspace || !file || uploading) return;

    setUploading(true);
    setError("");
    setNotice("");

    try {
      let source = sources[0];
      if (!source) {
        source = await api(`/api/v1/workspaces/${workspace.id}/sources`, {
          method: "POST",
          body: JSON.stringify({ name: "Uploaded documents", source_type: "file" }),
        });
      }

      const form = new FormData();
      form.append("file", file);

      const result = await api(`/api/v1/sources/${source.id}/upload`, {
        method: "POST",
        body: form,
      });

      setFile(null);
      setLastUpload({ title: result.title, chunks: result.chunks_created });
      setNotice(`Indexed “${result.title}” into ${result.chunks_created} knowledge chunks.`);
      await refresh(workspace.id, conversationId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function ask(event: FormEvent) {
    event.preventDefault();
    if (!workspace || !question.trim() || asking) return;

    const submittedQuestion = question.trim();
    setAsking(true);
    setError("");
    setNotice("");
    setAnswer("");
    setCitations([]);

    try {
      const data = await api(`/api/v1/workspaces/${workspace.id}/chat`, {
        method: "POST",
        body: JSON.stringify({
          question: submittedQuestion,
          conversation_id: conversationId,
        }),
      });

      setConversationId(data.conversation_id);
      setAnswer(data.answer);
      setCitations(data.citations || []);
      setMessages((old) => [
        ...old,
        { id: crypto.randomUUID(), role: "user", content: submittedQuestion },
        { id: crypto.randomUUID(), role: "assistant", content: data.answer },
      ]);

      setConversations((old) =>
        old.map((conversation) =>
          conversation.id === data.conversation_id
            ? { ...conversation, title: conversation.title || submittedQuestion.slice(0, 120) }
            : conversation
        )
      );

      if (!conversations.some((conversation) => conversation.id === data.conversation_id)) {
        setConversations((old) => [
          { id: data.conversation_id, workspace_id: workspace.id, title: submittedQuestion.slice(0, 120) },
          ...old,
        ]);
      }

      setQuestion("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setAsking(false);
    }
  }

  const busy = uploading || asking || creatingConversation;

  return (
    <div className="workspace-grid">
      <aside className="panel sidebar">
        <div className="panel-title">
          <div>
            <h2>Conversations</h2>
            <p className="panel-kicker">Independent research threads</p>
          </div>
          <button
            type="button"
            className="icon-btn"
            onClick={() => void newConversation()}
            disabled={!workspace || creatingConversation}
            aria-label="Start a new conversation"
            title="Start a new conversation"
          >
            +
          </button>
        </div>

        <div className="conversation-list">
          {conversations.length === 0 ? (
            <div className="empty-state">No threads yet. Start one with + or New thread.</div>
          ) : (
            conversations.map((conversation) => (
              <button
                type="button"
                key={conversation.id}
                onClick={() => void selectConversation(conversation.id)}
                className={`conversation ${conversationId === conversation.id ? "active" : ""}`}
                disabled={busy}
              >
                <span className="conversation-name">
                  {localTitle(conversation, conversation.id === conversationId ? messages : [])}
                </span>
                <span className="conversation-id">
                  {conversation.id.slice(0, 8)} · {conversation.id === conversationId ? "active" : "thread"}
                </span>
              </button>
            ))
          )}
        </div>

        <div className="divider" />

        <div className="panel-title">
          <div>
            <h2>Knowledge base</h2>
            <p className="panel-kicker">Ground answers in your files</p>
          </div>
        </div>

        <div
          className={`upload-zone ${dragging ? "dragging" : ""}`}
          onDragOver={(event) => {
            event.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
        >
          <input
            className="file-input"
            type="file"
            accept={SUPPORTED_EXTENSIONS}
            onChange={(event) => chooseFile(event.target.files?.[0] ?? null)}
            disabled={busy}
            aria-label="Choose a document to index"
          />

          <p className="panel-kicker">
            {dragging ? "Drop it here" : "Drag & drop or choose a document"}
          </p>

          {file && (
            <div className="file-name" title={file.name}>
              <span>Selected</span>
              <strong>{file.name}</strong>
            </div>
          )}

          {lastUpload && !file && (
            <div className="indexed-file">
              <span className="indexed-check">✓</span>
              <div>
                <strong>{lastUpload.title}</strong>
                <small>{lastUpload.chunks} chunks indexed</small>
              </div>
            </div>
          )}

          <div className="upload-actions">
            <button
              type="button"
              className="primary-btn"
              onClick={() => void upload()}
              disabled={!file || busy || !workspace}
            >
              {uploading ? "Indexing…" : "Upload & index"}
            </button>
            {file && (
              <button
                type="button"
                className="secondary-btn"
                onClick={() => setFile(null)}
                disabled={busy}
              >
                Clear
              </button>
            )}
          </div>
        </div>

        <p className="source-count">
          {sources.length} connected source{sources.length === 1 ? "" : "s"}
        </p>
        <p className="panel-kicker">AI: configurable Hugging Face Inference Providers</p>
      </aside>

      <section className="panel main-panel">
        <div className="chat-topbar">
          <div>
            <h2 className="chat-heading">
              {currentConversation ? currentConversation.title || "Knowledge chat" : "New knowledge chat"}
            </h2>
            <span className="chat-meta">
              {booting ? "Connecting to AtlasAI…" : workspace ? workspace.name : "Workspace unavailable"}
            </span>
          </div>

          <button
            type="button"
            className="secondary-btn"
            onClick={() => void newConversation()}
            disabled={!workspace || creatingConversation}
          >
            {creatingConversation ? "Creating…" : "New thread"}
          </button>
        </div>

        {error && <div className="error-banner">{error}</div>}
        {notice && <div className="info-banner">{notice}</div>}

        <div className="messages">
          {messages.length === 0 ? (
            <div className="welcome-card">
              <div className="welcome-icon">✦</div>
              <h3>{currentConversation ? "This thread is ready." : "Ask AtlasAI anything in your knowledge base."}</h3>
              <p>
                {currentConversation
                  ? "This is an independent conversation. Ask a question and its messages will stay inside this thread."
                  : "Upload a document on the left, then ask a precise question. AtlasAI retrieves relevant evidence and uses the configured AI model to synthesize a grounded answer."}
              </p>
            </div>
          ) : (
            messages.slice(-12).map((message) => (
              <div key={message.id} className={`message ${message.role === "user" ? "user" : ""}`}>
                <div className="avatar">{message.role === "user" ? "Y" : "A"}</div>
                <div className="bubble">{message.content}</div>
              </div>
            ))
          )}
        </div>

        <form onSubmit={ask} className="composer">
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder={workspace ? "Ask about your indexed knowledge…" : "Connecting to workspace…"}
            className="composer-input"
            disabled={busy || !workspace}
          />
          <button
            type="submit"
            disabled={busy || !workspace || !question.trim()}
            className="primary-btn send-btn"
          >
            {asking ? "Thinking…" : "Ask"}
          </button>
        </form>
      </section>

      <aside className="panel evidence-panel">
        <div className="evidence-header">
          <div>
            <h2 className="panel-title" style={{ margin: 0 }}>Evidence</h2>
            <p className="panel-kicker">Retrieved grounding signals</p>
          </div>
          <span className="status-pill">
            {citations.length} citation{citations.length === 1 ? "" : "s"}
          </span>
        </div>

        {answer && (
          <div className="answer-card">
            <h3>Latest grounded answer</h3>
            <p>{answer}</p>
          </div>
        )}

        {citations.length ? (
          <div className="evidence-list">
            {citations.map((citation, index) => (
              <div key={citation.chunk_id} className="citation-card">
                <div className="citation-top">
                  <span className="citation-label">SOURCE {index + 1}</span>
                  <span className="score">{citation.score.toFixed(3)} match</span>
                </div>
                <div className="citation-id">chunk {citation.chunk_id.slice(0, 12)}…</div>
                <div className="citation-id">document {citation.document_id.slice(0, 12)}…</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">Ask a question to inspect retrieved evidence and citation scores.</div>
        )}
      </aside>
    </div>
  );
}
