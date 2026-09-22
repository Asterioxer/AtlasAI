import ChatWorkspace from "./components/ChatWorkspace";

export default function Home() {
  return (
    <main className="mx-auto min-h-screen max-w-6xl p-8">
      <header className="mb-8">
        <p className="text-sm font-semibold tracking-wide">ATLASAI</p>
        <h1 className="mt-2 text-4xl font-semibold tracking-tight">Enterprise knowledge, grounded.</h1>
        <p className="mt-3 max-w-2xl text-zinc-600">Search your knowledge base, ask questions, and inspect the evidence behind responses.</p>
      </header>
      <ChatWorkspace />
    </main>
  );
}
