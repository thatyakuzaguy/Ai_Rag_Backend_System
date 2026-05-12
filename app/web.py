from fastapi.responses import HTMLResponse


def home_page() -> HTMLResponse:
    return HTMLResponse(
        """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI RAG Backend System</title>
  <style>
    :root {
      --bg: #fff8f8;
      --ink: #22191d;
      --muted: #725d67;
      --line: #ecd6de;
      --brand: #b84f74;
      --brand-dark: #803450;
      --soft: #fff0f4;
      --panel: rgba(255, 255, 255, 0.9);
      --night: #2b2027;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 84% 10%, rgba(232, 135, 164, 0.24), transparent 26%),
        linear-gradient(135deg, #fff7f8 0%, #fffdf9 48%, #fff1f5 100%);
    }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; }
    a { color: inherit; }
    .wrap { width: min(1120px, calc(100% - 36px)); margin: 0 auto; }
    .petal {
      position: fixed;
      width: 16px;
      height: 24px;
      border-radius: 70% 30% 70% 30%;
      background: rgba(232, 135, 164, 0.22);
      pointer-events: none;
      z-index: 0;
    }
    .p1 { left: 7%; top: 15%; transform: rotate(24deg); }
    .p2 { right: 11%; top: 22%; transform: rotate(-18deg); }
    .p3 { right: 7%; top: 66%; transform: rotate(48deg); }
    header {
      position: relative;
      z-index: 1;
      padding: 22px 0;
      border-bottom: 1px solid rgba(236, 214, 222, 0.7);
      background: rgba(255, 248, 248, 0.72);
      backdrop-filter: blur(12px);
    }
    nav { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
    .brand { font-weight: 950; font-size: 19px; color: var(--night); }
    .links { display: flex; gap: 10px; flex-wrap: wrap; }
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 42px;
      padding: 0 16px;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 850;
      background: var(--brand);
      color: white;
    }
    .btn:hover { background: var(--brand-dark); }
    .btn.secondary { background: #f2e3e9; color: #392832; }
    main { position: relative; z-index: 1; }
    .hero {
      min-height: 560px;
      display: grid;
      grid-template-columns: minmax(0, 1.08fr) minmax(320px, 0.92fr);
      gap: 28px;
      align-items: center;
      padding: 42px 0 32px;
    }
    .eyebrow {
      display: inline-flex;
      padding: 7px 11px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(255,255,255,0.72);
      color: var(--brand-dark);
      font-weight: 900;
      font-size: 13px;
    }
    h1 {
      margin: 18px 0 14px;
      max-width: 760px;
      font-size: clamp(44px, 7vw, 82px);
      line-height: 0.94;
      letter-spacing: 0;
    }
    .lead {
      max-width: 700px;
      color: var(--muted);
      font-size: 19px;
      line-height: 1.65;
    }
    .hero-actions { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 26px; }
    .terminal {
      border-radius: 14px;
      overflow: hidden;
      border: 1px solid #49353f;
      background: var(--night);
      box-shadow: 0 24px 70px rgba(90, 48, 64, 0.2);
    }
    .terminal-bar {
      display: flex;
      gap: 7px;
      padding: 14px;
      background: #3b2c35;
    }
    .dot { width: 11px; height: 11px; border-radius: 50%; background: #e88bab; }
    pre {
      margin: 0;
      padding: 22px;
      overflow: auto;
      color: #fff7fa;
      line-height: 1.55;
      font-size: 14px;
    }
    .section { padding: 34px 0; }
    .section-title {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: end;
      margin-bottom: 18px;
    }
    .section-title h2 { margin: 0; font-size: clamp(28px, 4vw, 42px); }
    .section-title p { margin: 0; max-width: 560px; color: var(--muted); line-height: 1.6; }
    .grid { display: grid; gap: 16px; }
    .cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .card {
      min-height: 150px;
      padding: 20px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: var(--panel);
      box-shadow: 0 18px 44px rgba(90, 48, 64, 0.08);
    }
    .card h3 { margin: 0 0 10px; font-size: 18px; }
    .card p, .card li { color: var(--muted); line-height: 1.58; }
    .card ul { margin: 0; padding-left: 18px; }
    .flow {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
    }
    .step {
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #fffdfd;
      padding: 16px;
    }
    .step strong { display: block; margin-bottom: 8px; color: var(--brand-dark); }
    .stack {
      display: flex;
      gap: 9px;
      flex-wrap: wrap;
    }
    .pill {
      padding: 8px 11px;
      border-radius: 999px;
      background: var(--soft);
      border: 1px solid var(--line);
      font-weight: 850;
      color: #4d3340;
    }
    footer {
      margin-top: 42px;
      padding: 28px 0;
      border-top: 1px solid var(--line);
      color: var(--muted);
    }
    @media (max-width: 900px) {
      .hero, .cols-3, .cols-2, .flow { grid-template-columns: 1fr; }
      .hero { min-height: auto; }
      .section-title { display: block; }
      nav { align-items: flex-start; flex-direction: column; }
    }
  </style>
</head>
<body>
  <span class="petal p1"></span><span class="petal p2"></span><span class="petal p3"></span>
  <header>
    <nav class="wrap">
      <div class="brand">AI RAG Backend System</div>
      <div class="links">
        <a class="btn secondary" href="/docs">Swagger Docs</a>
        <a class="btn secondary" href="/health">Health Check</a>
        <a class="btn" href="https://github.com/thatyakuzaguy/Ai_Rag_Backend_System">GitHub</a>
      </div>
    </nav>
  </header>

  <main>
    <section class="wrap hero">
      <div>
        <span class="eyebrow">FastAPI RAG portfolio project</span>
        <h1>Backend system for searchable, cited knowledge.</h1>
        <p class="lead">
          A deployed Retrieval-Augmented Generation API with authentication, collections,
          document ingestion, vector search, conversation storage, feedback, tests, and
          Render-ready Docker deployment.
        </p>
        <div class="hero-actions">
          <a class="btn" href="/docs">Inspect the API</a>
          <a class="btn secondary" href="https://github.com/thatyakuzaguy/Ai_Rag_Backend_System">View source</a>
        </div>
      </div>
      <div class="terminal" aria-label="API preview">
        <div class="terminal-bar"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>
<pre>POST /auth/register
POST /collections
POST /collections/{id}/documents
POST /collections/{id}/chat

Security:
- bearer tokens
- scoped collections
- parameterized SQL
- input validation
- regression tests</pre>
      </div>
    </section>

    <section class="wrap section">
      <div class="section-title">
        <h2>What It Can Do</h2>
        <p>The homepage is a showcase, while the backend remains fully testable through Swagger and the repository.</p>
      </div>
      <div class="grid cols-3">
        <article class="card">
          <h3>Ingest Knowledge</h3>
          <p>Accepts raw text and files, chunks content with overlap, and stores metadata for later retrieval.</p>
        </article>
        <article class="card">
          <h3>Retrieve Context</h3>
          <p>Embeds queries, compares vectors with cosine similarity, and returns the most relevant chunks.</p>
        </article>
        <article class="card">
          <h3>Answer With Citations</h3>
          <p>Combines retrieved context with local or OpenAI providers and returns source-backed responses.</p>
        </article>
      </div>
    </section>

    <section class="wrap section">
      <div class="section-title">
        <h2>Architecture</h2>
        <p>Designed as a backend-first system with clean service boundaries and realistic portfolio features.</p>
      </div>
      <div class="flow">
        <div class="step"><strong>1. API</strong>FastAPI routes validate requests and expose REST endpoints.</div>
        <div class="step"><strong>2. Services</strong>RAG, auth, storage, and provider logic stay separated.</div>
        <div class="step"><strong>3. Storage</strong>SQLite persists users, tokens, collections, chats, and vectors.</div>
        <div class="step"><strong>4. Retrieval</strong>Embeddings and filters isolate the correct collection context.</div>
        <div class="step"><strong>5. Response</strong>Answers include citations and stored conversation history.</div>
      </div>
    </section>

    <section class="wrap section">
      <div class="grid cols-2">
        <article class="card">
          <h3>Security Work</h3>
          <ul>
            <li>Protected write endpoints with bearer authentication.</li>
            <li>Hashed API tokens and password hashing.</li>
            <li>Collection ownership checks for multi-user isolation.</li>
            <li>Parameterized SQL with injection regression tests.</li>
          </ul>
        </article>
        <article class="card">
          <h3>Engineering Proof</h3>
          <ul>
            <li>Pytest coverage for API, RAG behavior, auth, and SQL safety.</li>
            <li>Ruff linting and compile checks.</li>
            <li>Dockerfile configured for Render deployment.</li>
            <li>Free local provider mode plus optional OpenAI provider mode.</li>
          </ul>
        </article>
      </div>
    </section>

    <section class="wrap section">
      <div class="section-title">
        <h2>Tech Stack</h2>
        <p>Simple, inspectable tools chosen for a portfolio demo that can run without paid infrastructure.</p>
      </div>
      <div class="stack">
        <span class="pill">Python</span>
        <span class="pill">FastAPI</span>
        <span class="pill">Pydantic</span>
        <span class="pill">SQLite</span>
        <span class="pill">Vector Search</span>
        <span class="pill">Pytest</span>
        <span class="pill">Ruff</span>
        <span class="pill">Docker</span>
        <span class="pill">Render</span>
      </div>
    </section>
  </main>

  <footer>
    <div class="wrap">Built as a backend portfolio project focused on practical RAG, API design, and deployment readiness.</div>
  </footer>
</body>
</html>
        """
    )
