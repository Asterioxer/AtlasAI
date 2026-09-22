"use client";

import { FormEvent, useState } from "react";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  async function ask(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1/workspaces/demo/chat`,
        { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question }) },
      );
      const data = await response.json();
      setAnswer(data.answer ?? data.detail ?? "No response");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-4xl flex-col gap-8 p-8">
      <section>
        <p className="text-sm font-medium">AtlasAI</p>
        <h1 className="mt-2 text-4xl font-semibold">Enterprise knowledge, grounded.</h1>
        <p className="mt-3 text-zinc-600">Ask the knowledge system and receive a grounded response with citations.</p>
      </section>
      <form onSubmit={ask} className="flex flex-col gap-3">
        <textarea value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask AtlasAI..." className="min-h-40 rounded-xl border p-4" />
        <button disabled={loading} className="rounded-xl border px-4 py-3 text-left">{loading ? "Thinking..." : "Ask AtlasAI"}</button>
      </form>
      {answer && <section className="rounded-xl border p-5"><h2 className="font-semibold">Answer</h2><p className="mt-3 whitespace-pre-wrap">{answer}</p></section>}
    </main>
  );
}
