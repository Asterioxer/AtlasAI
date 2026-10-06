import ChatWorkspace from "./components/ChatWorkspace";

export default function Home() {
  return (
    <main className="atlas-shell">
      <header className="atlas-header">
        <div>
          <div className="brand-row">
            <div className="brand-mark">A</div>
            <div>
              <p className="eyebrow">ATLASAI</p>
              <h1 className="atlas-title">Enterprise knowledge, grounded.</h1>
            </div>
          </div>
          <p className="atlas-subtitle">
            Search your knowledge base, ask questions, and inspect the evidence behind every response.
          </p>
        </div>
        <div className="status-pill"><span className="status-dot online" /> Local workspace</div>
      </header>
      <ChatWorkspace />
    </main>
  );
}
