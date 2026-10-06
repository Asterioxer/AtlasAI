"use client";

import { FormEvent, useEffect, useState } from "react";

type Workspace = { id: string; name: string };
type Source = { id: string; name: string; source_type: string };
type Conversation = { id: string; workspace_id: string };
type Message = { id: string; role: string; content: string };
type Citation = { chunk_id: string; source_id: string; document_id: string; score: number };

const API =
  process.env.NEXT_PUBLIC_API_URL ??
  (typeof window !== "undefined" && window.location.hostname !== "localhost"
    ? "https://atlasai-w5i8.onrender.com"
    : "http://localhost:8000");
const TOKEN = process.env.NEXT_PUBLIC_ATLAS_TOKEN ?? "demo-user";

async function api(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${TOKEN}`);
  if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const response = await fetch(`${API}${path}`, { ...init, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail ?? "Request failed");
  return data;
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
  const [error, setError] = useState("");

  async function refresh(id: string) {
    const [sourceRows, conversationRows] = await Promise.all([
      api(`/api/v1/workspaces/${id}/sources`),
      api(`/api/v1/workspaces/${id}/conversations`),
    ]);
    setSources(sourceRows);
    setConversations(conversationRows);
    if (!conversationId && conversationRows[0]) selectConversation(conversationRows[0].id);
  }

  useEffect(() => {
    (async () => {
      try {
        const rows = await api("/api/v1/workspaces");
        const current: Workspace = rows[0] ?? await api("/api/v1/workspaces", { method: "POST", body: JSON.stringify({ name: "AtlasAI Demo" }) });
        setWorkspace(current);
        await refresh(current.id);
      } catch (e) { setError(e instanceof Error ? e.message : "Failed to initialize workspace"); }
    })();
  }, []);

  async function selectConversation(id: string) {
    setConversationId(id);
    try {
      const rows = await api(`/api/v1/conversations/${id}/messages`);
      setMessages(rows);
    } catch (e) { setError(e instanceof Error ? e.message : "Failed to load conversation"); }
  }

  async function newConversation() {
    if (!workspace) return;
    const row = await api(`/api/v1/workspaces/${workspace.id}/conversations`, { method: "POST" });
    setConversations((old) => [row, ...old]);
    await selectConversation(row.id);
  }

  async function upload() {
    if (!workspace || !file) return;
    setLoading(true); setError("");
    try {
      let source = sources[0];
      if (!source) {
        source = await api(`/api/v1/workspaces/${workspace.id}/sources`, {
          method: "POST", body: JSON.stringify({ name: "Uploaded documents", source_type: "file" }),
        });
      }
      const form = new FormData();
      form.append("file", file);
      await api(`/api/v1/sources/${source.id}/upload`, { method: "POST", body: form });
      setFile(null);
      await refresh(workspace.id);
    } catch (e) { setError(e instanceof Error ? e.message : "Upload failed"); }
    finally { setLoading(false); }
  }

  async function ask(event: FormEvent) {
    event.preventDefault();
    if (!workspace || !question.trim()) return;
    setLoading(true); setError(""); setAnswer(""); setCitations([]);
    try {
      const data = await api(`/api/v1/workspaces/${workspace.id}/chat`, {
        method: "POST",
        body: JSON.stringify({ question, conversation_id: conversationId }),
      });
      setConversationId(data.conversation_id);
      setAnswer(data.answer);
      setCitations(data.citations ?? []);
      setMessages((old) => [
        ...old,
        { id: crypto.randomUUID(), role: "user", content: question },
        { id: crypto.randomUUID(), role: "assistant", content: data.answer },
      ]);
      if (!conversations.some((c) => c.id === data.conversation_id)) {
        setConversations((old) => [{ id: data.conversation_id, workspace_id: workspace.id }, ...old]);
      }
      setQuestion("");
    } catch (e) { setError(e instanceof Error ? e.message : "Request failed"); }
    finally { setLoading(false); }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[240px_1fr_300px]">
      <aside className="rounded-xl border p-4">
        <div className="flex items-center justify-between"><h2 className="font-semibold">Conversations</h2><button onClick={newConversation} className="rounded border px-2 py-1 text-sm">+</button></div>
        <div className="mt-3 space-y-2">
          {conversations.map((c) => <button key={c.id} onClick={() => selectConversation(c.id)} className={`block w-full truncate rounded-lg border p-2 text-left text-sm ${conversationId === c.id ? "bg-zinc-100" : ""}`}>{c.id.slice(0, 8)}</button>)}
        </div>
        <div className="mt-6 border-t pt-4">
          <h2 className="font-semibold">Knowledge base</h2>
          <input type="file" accept=".txt,.md,.markdown,.pdf" onChange={(e) => setFile(e.target.files?.[0] ?? null)} className="mt-3 w-full text-sm" />
          <button onClick={upload} disabled={!file || loading} className="mt-2 w-full rounded-lg border px-3 py-2 text-sm">{loading ? "Working..." : "Upload document"}</button>
          <p className="mt-2 text-xs text-zinc-500">{sources.length} source(s) connected.</p>
        </div>
      </aside>
      <section>
        <form onSubmit={ask} className="flex gap-3">
          <input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask your knowledge base..." className="min-w-0 flex-1 rounded-xl border px-4 py-3" />
          <button disabled={loading || !workspace} className="rounded-xl border px-5 py-3 font-medium">{loading ? "..." : "Ask"}</button>
        </form>
        {error && <p className="mt-4 rounded-lg border p-3 text-sm">{error}</p>}
        {messages.length > 0 && <div className="mt-6 space-y-3">{messages.slice(-8).map((m) => <div key={m.id} className="rounded-xl border p-4"><div className="text-xs font-semibold uppercase text-zinc-500">{m.role}</div><p className="mt-2 whitespace-pre-wrap">{m.content}</p></div>)}</div>}
        {answer && <article className="mt-6 rounded-xl border p-6"><h2 className="font-semibold">Latest grounded answer</h2><p className="mt-3 whitespace-pre-wrap leading-7">{answer}</p></article>}
      </section>
      <aside className="rounded-xl border p-5">
        <h2 className="font-semibold">Evidence</h2>
        {citations.length ? <ul className="mt-3 space-y-2">{citations.map((c) => <li key={c.chunk_id} className="rounded-lg border p-3 text-sm"><b>{c.chunk_id.slice(0, 8)}</b><div className="text-zinc-500">score {c.score.toFixed(3)}</div></li>)}</ul> : <p className="mt-3 text-sm text-zinc-500">Ask a question to inspect retrieved evidence.</p>}
      </aside>
    </div>
  );
}
