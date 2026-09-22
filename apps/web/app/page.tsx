"use client";

import { FormEvent, useState } from "react";

type Citation = { chunk_id: string; source_id: string; document_id: string; score: number };

export default function Home() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [loading, setLoading] = useState(false);
  const api = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  async function ask(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setAnswer("");
    setCitations([]);
    try {
      const response = await fetch(`${api}/api/v1/workspaces/demo/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Request failed");
      setAnswer(data.answer);
      setCitations(data.citations ?? []);
    } catch (error) {
      setAnswer(error instanceof Error ? error.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col gap-8 p-8">
      <header>
        <p className="text-sm font-semibold tracking-wide">ATLASAI</p>
        <h1 className="mt-2 text-4xl font-semibold tracking-tight">Enterprise knowledge, grounded.</h1>
        <p className="mt-3 max-w-2xl text-zinc-600">Ask questions against your knowledge base and inspect the evidence behind every answer.</p>
      </header>
      <form onSubmit={ask} className="flex flex-col gap-3">
        <textarea value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask a question..." className="min-h-36 rounded-xl border p-4 outline-none focus:ring-2" />
        <button disabled={loading} className="rounded-xl border px-4 py-3 font-medium disabled:opacity-50">{loading ? "Thinking..." : "Ask AtlasAI"}</button>
      </form>
      {answer && (
        <section className="grid gap-5 md:grid-cols-[1fr_280px]">
          <article className="rounded-xl border p-6">
            <h2 className="font-semibold">Answer</h2>
            <p className="mt-3 whitespace-pre-wrap leading-7">{answer}</p>
          </article>
          <aside className="rounded-xl border p-5">
            <h2 className="font-semibold">Citations</h2>
            {citations.length === 0 ? <p className="mt-3 text-sm text-zinc-500">No retrieved evidence yet.</p> : (
              <ul className="mt-3 space-y-3 text-sm">
                {citations.map((citation) => <li key={citation.chunk_id} className="rounded-lg border p-3"><div className="font-medium">{citation.chunk_id}</div><div className="text-zinc-500">Score {citation.score.toFixed(3)}</div></li>)}
              </ul>
            )}
          </aside>
        </section>
      )}
    </main>
  );
}
