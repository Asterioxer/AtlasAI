"use client";

import { FormEvent, useState } from "react";

type Citation = { chunk_id: string; source_id: string; document_id: string; score: number };

export default function ChatWorkspace() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [loading, setLoading] = useState(false);

  async function ask(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setAnswer("");
    setCitations([]);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/workspaces/demo/chat`,
        { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question }) },
      );
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Request failed");
      setAnswer(data.answer ?? "");
      setCitations(data.citations ?? []);
    } catch (error) {
      setAnswer(error instanceof Error ? error.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
      <section>
        <form onSubmit={ask} className="flex gap-3">
          <input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask your knowledge base..." className="min-w-0 flex-1 rounded-xl border px-4 py-3" />
          <button disabled={loading} className="rounded-xl border px-5 py-3 font-medium">{loading ? "..." : "Ask"}</button>
        </form>
        {answer && <article className="mt-6 rounded-xl border p-6"><h2 className="font-semibold">Answer</h2><p className="mt-3 whitespace-pre-wrap leading-7">{answer}</p></article>}
      </section>
      <aside className="rounded-xl border p-5">
        <h2 className="font-semibold">Evidence</h2>
        {citations.length ? <ul className="mt-3 space-y-2">{citations.map((c) => <li key={c.chunk_id} className="rounded-lg border p-3 text-sm"><b>{c.chunk_id}</b><div className="text-zinc-500">score {c.score.toFixed(3)}</div></li>)}</ul> : <p className="mt-3 text-sm text-zinc-500">Citations appear here.</p>}
      </aside>
    </div>
  );
}
