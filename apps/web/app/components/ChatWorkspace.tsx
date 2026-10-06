"use client";

import { DragEvent, FormEvent, useEffect, useMemo, useState } from "react";

type Workspace = { id: string; name: string };
type Source = { id: string; name: string; source_type: string };
type Conversation = { id: string; workspace_id: string };
type Message = { id: string; role: string; content: string };
type Citation = { chunk_id: string; source_id: string; document_id: string; score: number };

const API =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" && window.location.hostname !== "localhost"
    ? "https://atlasai-w5i8.onrender.com"
    : "http://localhost:8000");
const TOKEN = process.env.NEXT_PUBLIC_ATLAS_TOKEN || "demo-user";

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

function conversationLabel(id: string, messages: Message[], fallbackIndex: number) {
  const firstUser = messages.find((m) => m.role === "user");
  if (firstUser?.content) return firstUser.content.slice(0, 34) + (firstUser.content.length > 34 ? "…" : "");
  return `Conversation ${fallbackIndex + 1}`;
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
  const [loading, setLoading] = useState(false);
  const [booting, setBooting] = useState(true);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");

  const currentConversation = useMemo(
    () => conversations.find((c) => c.id === conversationId),
    [conversations, conversationId]
  );

  async function selectConversation(id: string) {
    setConversationId(id);
    setAnswer("");
    setCitations([]);
    setError("");
    try {
      const rows = await api(`/api/v1/conversations/${id}/messages`);
      setMessages(rows);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load conversation");
    }
  }

  async function refresh(id: string, preferConversation = false) {
    const [sourceRows, conversationRows] = await Promise.all([
      api(`/api/v1/workspaces/${id}/sources`),
      api(`/api/v1/workspaces/${id}/conversations`),
    ]);
    setSources(sourceRows);
    setConversations(conversationRows);

    if (preferConversation && conversationRows[0]) {
      await selectConversation(conversationRows[0].id);
    } else if (!conversationId && conversationRows[0]) {
      await selectConversation(conversationRows[0].id);
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
    // The API/workspace should initialize once when the page mounts.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function newConversation() {
    if (!workspace) return;
    setError("");
    try {
      const row = await api(`/api/v1/workspaces/${workspace.id}/conversations`, { method: "POST" });
      setConversations((old) => [row, ...old]);
      await selectConversation(row.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not create conversation");
    }
  }

  function chooseFile(nextFile: File | null) {
    if (!nextFile) return;
    const allowed = ["application/pdf", "text/plain", "text/markdown"];
    const extensionOk = /\.(pdf|txt|md|markdown)$/i.test(nextFile.name);
    if (!extensionOk && !allowed.includes(nextFile.type)) {
      setError("Use a PDF, Markdown, or TXT document.");
      return;
    }
    setError("");
    setFile(nextFile);
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragging(false);
    chooseFile(event.dataTransfer.files?.[0] ?? null);
  }

  async function upload() {
    if (!workspace || !file) return;
    setLoading(true);
    setError("");
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
      await refresh(workspace.id);
      setError(`Uploaded “${result.title}” — ${result.chunks_created} chunks indexed.`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  async function ask(event: FormEvent) {
    event.preventDefault();
    if (!workspace || !question.trim() || loading) return;

    const submittedQuestion = question.trim();
    setLoading(true);
    setError("");
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

      if (!conversations.some((c) => c.id === data.conversation_id)) {
        setConversations((old) => [
          { id: data.conversation_id, workspace_id: workspace.id },
          ...old,
        ]);
      }
      setQuestion("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="workspace-grid">
      <aside className="panel sidebar">
        <div className="panel-title">
          <div>
            <h2>Conversations</h2>
            <p className="panel-kicker">Your research threads</p>
          </div>
          <button
            type="button"
            className="icon-btn"
            onClick={newConversation}
            disabled={!workspace || loading}
            aria-label="New conversation"
            title="New conversation"
          >
            +
          </button>
        </div>

        <div className="conversation-list">
          {conversations.length === 0 ? (
            <div className="empty-state">No conversations yet. Start a new thread.</div>
          ) : (
            conversations.map((conversation, index) => (
              <button
                type="button"
                key={conversation.id}
                onClick={() => void selectConversation(conversation.id)}
                className={`conversation ${conversationId === conversation.id ? "active" : ""}`}
              >
                <span className="conversation-name">
                  {conversation.id === conversationId
                    ? conversationLabel(conversation.id, messages, index)
                    : `Conversation ${index + 1}`}
                </span>
                <span className="conversation-id">{conversation.id.slice(0, 8)} · synced</span>
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
            accept=".txt,.md,.markdown,.pdf"
            onChange={(event) => chooseFile(event.target.files?.[0] ?? null)}
            disabled={loading}
          />
          <p className="panel-kicker">{dragging ? "Drop it here" : "Drag & drop or choose a document"}</p>
          {file && <div className="file-name" title={file.name}>{file.name}</div>}
          <div className="upload-actions">
            <button
              type="button"
              className="primary-btn"
              onClick={() => void upload()}
              disabled={!file || loading || !workspace}
            >
              {loading ? "Indexing…" : "Upload & index"}
            </button>
            {file && (
              <button type="button" className="secondary-btn" onClick={() => setFile(null)} disabled={loading}>
                Clear
              </button>
            )}
          </div>
        </div>
        <p className="source-count">{sources.length} connected source{sources.length === 1 ? "" : "s"}</p>
      </aside>

      <section className="panel main-panel">
        <div className="chat-topbar">
          <div>
            <h2 className="chat-heading">{currentConversation ? "Knowledge chat" : "New knowledge chat"}</h2>
            <span className="chat-meta">
              {booting ? "Connecting to AtlasAI…" : workspace ? workspace.name : "Workspace unavailable"}
            </span>
          </div>
          {currentConversation && <button className="secondary-btn" onClick={() => void newConversation()}>New thread</button>}
        </div>

        {error && (
          <div className={error.startsWith("Uploaded") ? "info-banner" : "error-banner"}>
            {error}
            {!error.startsWith("Uploaded") && (
              <button
                type="button"
                className="secondary-btn"
                style={{ marginLeft: 8, padding: "4px 8px" }}
                onClick={() => void initialize()}
              >
                Retry
              </button>
            )}
          </div>
        )}

        <div className="messages">
          {messages.length === 0 ? (
            <div className="welcome-card">
              <div className="welcome-icon">✦</div>
              <h3>Ask AtlasAI anything in your knowledge base.</h3>
              <p>
                Upload a document on the left, then ask a precise question. AtlasAI will retrieve
                relevant evidence and show the sources behind its answer.
              </p>
            </div>
          ) : (
            messages.slice(-10).map((message) => (
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
            disabled={loading || !workspace}
          />
          <button
            type="submit"
            disabled={loading || !workspace || !question.trim()}
            className="primary-btn send-btn"
          >
            {loading ? "Thinking…" : "Ask"}
          </button>
        </form>
      </section>

      <aside className="panel evidence-panel">
        <div className="evidence-header">
          <div>
            <h2 className="panel-title" style={{ margin: 0 }}>Evidence</h2>
            <p className="panel-kicker">Retrieved grounding signals</p>
          </div>
          <span className="status-pill">{citations.length} citation{citations.length === 1 ? "" : "s"}</span>
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
