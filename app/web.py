from fastapi.responses import HTMLResponse


def home_page() -> HTMLResponse:
    return HTMLResponse(
        """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>KnowledgeBase AI</title>
  <style>
    :root {
      --bg: #f4f6f8;
      --panel: #ffffff;
      --ink: #161a22;
      --muted: #667085;
      --line: #dce2ea;
      --brand: #0f6b7a;
      --brand-dark: #0a4e5a;
      --soft: #edf7f8;
      --danger: #b42318;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }
    * { box-sizing: border-box; }
    body { margin: 0; }
    button, input, textarea { font: inherit; }
    button {
      min-height: 40px;
      border: 0;
      border-radius: 6px;
      padding: 0 14px;
      background: var(--brand);
      color: #fff;
      font-weight: 800;
      cursor: pointer;
    }
    button:hover { background: var(--brand-dark); }
    button.secondary { background: #e8edf3; color: #26323f; }
    button.secondary:hover { background: #d8e0e8; }
    input, textarea, select {
      width: 100%;
      border: 1px solid #cbd4df;
      border-radius: 6px;
      padding: 10px 12px;
      background: #fff;
      color: var(--ink);
    }
    textarea { min-height: 150px; resize: vertical; }
    label { display: block; margin: 12px 0 6px; font-size: 13px; font-weight: 800; color: #344054; }
    .shell { display: grid; grid-template-columns: 280px 1fr; min-height: 100vh; }
    aside {
      border-right: 1px solid var(--line);
      background: #111820;
      color: #ecf1f4;
      padding: 22px;
    }
    .brand { font-size: 22px; font-weight: 900; letter-spacing: 0; margin-bottom: 8px; }
    .tagline { color: #b5c0cc; line-height: 1.5; margin: 0 0 22px; }
    nav { display: grid; gap: 8px; margin-top: 20px; }
    nav a {
      color: #d9e3ea;
      text-decoration: none;
      padding: 10px 12px;
      border-radius: 6px;
      background: rgba(255,255,255,0.06);
    }
    nav a:hover { background: rgba(255,255,255,0.12); }
    main { padding: 26px; }
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 22px;
    }
    h1 { margin: 0; font-size: 30px; line-height: 1.1; }
    h2 { margin: 0 0 14px; font-size: 18px; }
    h3 { margin: 0 0 8px; font-size: 15px; }
    .muted { color: var(--muted); }
    .grid { display: grid; gap: 16px; }
    .cols-2 { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); }
    .cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }
    .metric strong { display: block; font-size: 28px; }
    .metric span { color: var(--muted); font-size: 13px; }
    .toolbar { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .collection-list, .doc-list, .chat-log { display: grid; gap: 10px; }
    .item {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fbfcfd;
    }
    .item.active { border-color: var(--brand); background: var(--soft); }
    .item button { margin-top: 10px; }
    .chat-log {
      min-height: 320px;
      max-height: 520px;
      overflow: auto;
      padding: 12px;
      background: #f7f9fb;
      border: 1px solid var(--line);
      border-radius: 8px;
    }
    .bubble {
      max-width: 82%;
      padding: 12px 14px;
      border-radius: 8px;
      line-height: 1.5;
      white-space: pre-wrap;
    }
    .bubble.user { justify-self: end; background: var(--brand); color: white; }
    .bubble.assistant { justify-self: start; background: #ffffff; border: 1px solid var(--line); }
    .notice {
      padding: 10px 12px;
      border-radius: 6px;
      background: #fff7e6;
      color: #7a4b00;
      border: 1px solid #ffd591;
    }
    .error { color: var(--danger); }
    .hidden { display: none !important; }
    .auth {
      max-width: 980px;
      margin: 46px auto;
      display: grid;
      grid-template-columns: 1fr 430px;
      gap: 24px;
      padding: 0 20px;
    }
    .auth-hero {
      padding: 34px;
      border-radius: 8px;
      background: #101820;
      color: #eef6f8;
      min-height: 460px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .auth-hero h1 { font-size: 44px; }
    .auth-card { background: white; border: 1px solid var(--line); border-radius: 8px; padding: 22px; }
    @media (max-width: 980px) {
      .shell { grid-template-columns: 1fr; }
      aside { position: static; }
      .cols-2, .cols-4, .auth { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <section id="auth-view" class="auth">
    <div class="auth-hero">
      <div>
        <div class="brand">KnowledgeBase AI</div>
        <h1>Chat with your documents.</h1>
        <p class="tagline">A FastAPI RAG workspace with document ingestion, collections, citations, chat history, and free local AI providers for portfolio demos.</p>
      </div>
      <div class="grid cols-2">
        <div><strong>RAG</strong><p class="tagline">Retrieve context before answering.</p></div>
        <div><strong>Cost aware</strong><p class="tagline">Runs without paid AI APIs by default.</p></div>
      </div>
    </div>
    <div class="auth-card">
      <h2>Access workspace</h2>
      <p class="muted">Create a demo account or sign in to your existing workspace.</p>
      <label>Email</label>
      <input id="auth-email" value="demo@example.com" />
      <label>Password</label>
      <input id="auth-password" type="password" placeholder="At least 8 characters" />
      <label>Display name</label>
      <input id="auth-name" value="Demo User" />
      <div class="toolbar" style="margin-top:16px">
        <button id="register-btn">Create account</button>
        <button id="login-btn" class="secondary">Sign in</button>
      </div>
      <p id="auth-error" class="error"></p>
    </div>
  </section>

  <section id="app-view" class="shell hidden">
    <aside>
      <div class="brand">KnowledgeBase AI</div>
      <p class="tagline">Private document collections with grounded answers and citations.</p>
      <div class="notice">Free demo mode uses local retrieval and extractive answers.</div>
      <nav>
        <a href="#dashboard">Dashboard</a>
        <a href="#collections">Collections</a>
        <a href="#chat">Chat</a>
        <a href="/docs">API Docs</a>
      </nav>
    </aside>

    <main>
      <header>
        <div>
          <h1>Workspace</h1>
          <p id="user-line" class="muted"></p>
        </div>
        <button id="logout-btn" class="secondary">Log out</button>
      </header>

      <section id="dashboard" class="grid cols-4" style="margin-bottom:16px">
        <div class="panel metric"><strong id="metric-collections">0</strong><span>Collections</span></div>
        <div class="panel metric"><strong id="metric-documents">0</strong><span>Documents</span></div>
        <div class="panel metric"><strong id="metric-chats">0</strong><span>Chats</span></div>
        <div class="panel metric"><strong id="metric-messages">0</strong><span>Messages</span></div>
      </section>

      <section class="grid cols-2">
        <div id="collections" class="panel">
          <h2>Collections</h2>
          <label>Name</label>
          <input id="collection-name" value="Python Notes" />
          <label>Description</label>
          <input id="collection-description" value="Python and backend learning notes" />
          <button id="create-collection-btn">Create collection</button>
          <div id="collection-list" class="collection-list" style="margin-top:16px"></div>
        </div>

        <div class="panel">
          <h2>Documents</h2>
          <p id="selected-collection-label" class="muted">Select a collection first.</p>
          <label>Source</label>
          <input id="document-source" value="python-basics-note" />
          <label>Text</label>
          <textarea id="document-text">A Python tuple is immutable. A list is mutable. FastAPI is used to build APIs with Python.</textarea>
          <button id="ingest-doc-btn">Ingest document</button>
          <div id="doc-list" class="doc-list" style="margin-top:16px"></div>
        </div>
      </section>

      <section id="chat" class="panel" style="margin-top:16px">
        <div class="toolbar" style="justify-content:space-between">
          <div>
            <h2>Collection Chat</h2>
            <p class="muted">Ask questions against the selected collection. The backend stores chat history.</p>
          </div>
          <button id="new-chat-btn" class="secondary">New chat</button>
        </div>
        <div id="chat-log" class="chat-log"></div>
        <label>Question</label>
        <div class="toolbar">
          <input id="chat-question" value="Is a tuple mutable?" />
          <button id="ask-btn">Ask</button>
        </div>
        <p id="app-error" class="error"></p>
      </section>
    </main>
  </section>

  <script>
    const state = {
      token: localStorage.getItem("kb_token"),
      user: JSON.parse(localStorage.getItem("kb_user") || "null"),
      collections: [],
      selectedCollectionId: localStorage.getItem("kb_collection"),
      sessionId: localStorage.getItem("kb_session"),
    };
    const $ = (id) => document.getElementById(id);

    async function api(path, options = {}) {
      const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
      if (state.token) headers.Authorization = `Bearer ${state.token}`;
      const response = await fetch(path, { ...options, headers });
      const text = await response.text();
      let body;
      try { body = JSON.parse(text); } catch { body = text; }
      if (!response.ok) throw new Error(body.detail || body || `HTTP ${response.status}`);
      return body;
    }

    function showAppError(error) { $("app-error").textContent = error.message || String(error); }
    function showAuthError(error) { $("auth-error").textContent = error.message || String(error); }
    function escapeHtml(value) {
      return String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
    }

    function setAuth(auth) {
      state.token = auth.token;
      state.user = auth.user;
      localStorage.setItem("kb_token", auth.token);
      localStorage.setItem("kb_user", JSON.stringify(auth.user));
      renderShell();
      refreshAll();
    }

    function renderShell() {
      $("auth-view").classList.toggle("hidden", Boolean(state.token));
      $("app-view").classList.toggle("hidden", !state.token);
      if (state.user) $("user-line").textContent = `${state.user.display_name} - ${state.user.email}`;
    }

    async function refreshAll() {
      if (!state.token) return;
      await Promise.all([loadMetrics(), loadCollections()]);
      if (state.selectedCollectionId) {
        await loadDocuments();
      }
    }

    async function loadMetrics() {
      const data = await api("/dashboard");
      $("metric-collections").textContent = data.collections;
      $("metric-documents").textContent = data.documents;
      $("metric-chats").textContent = data.chats;
      $("metric-messages").textContent = data.messages;
    }

    async function loadCollections() {
      state.collections = await api("/collections");
      $("collection-list").innerHTML = state.collections.map((collection) => `
        <div class="item ${collection.id === state.selectedCollectionId ? "active" : ""}">
          <h3>${escapeHtml(collection.name)}</h3>
          <p class="muted">${escapeHtml(collection.description || "No description")}</p>
          <p class="muted">${collection.document_count} documents - ${collection.chat_count} chats</p>
          <button class="secondary" data-select="${collection.id}">Select</button>
        </div>
      `).join("") || `<p class="muted">No collections yet.</p>`;
      document.querySelectorAll("[data-select]").forEach((button) => {
        button.addEventListener("click", async () => {
          state.selectedCollectionId = button.dataset.select;
          state.sessionId = null;
          localStorage.setItem("kb_collection", state.selectedCollectionId);
          localStorage.removeItem("kb_session");
          renderCollections();
          await loadDocuments();
        });
      });
      renderCollections();
    }

    function renderCollections() {
      const selected = state.collections.find((item) => item.id === state.selectedCollectionId);
      $("selected-collection-label").textContent = selected
        ? `Selected: ${selected.name}`
        : "Select a collection first.";
    }

    async function loadDocuments() {
      if (!state.selectedCollectionId) return;
      const docs = await api(`/collections/${state.selectedCollectionId}/documents`);
      $("doc-list").innerHTML = docs.map((doc) => `
        <div class="item">
          <h3>${escapeHtml(doc.source)}</h3>
          <p class="muted">${doc.chunks_indexed} chunks indexed</p>
        </div>
      `).join("") || `<p class="muted">No documents in this collection.</p>`;
    }

    function addBubble(role, content) {
      const div = document.createElement("div");
      div.className = `bubble ${role}`;
      div.textContent = content;
      $("chat-log").appendChild(div);
      $("chat-log").scrollTop = $("chat-log").scrollHeight;
    }

    $("register-btn").addEventListener("click", async () => {
      try {
        const auth = await api("/auth/register", {
          method: "POST",
          body: JSON.stringify({
            email: $("auth-email").value,
            password: $("auth-password").value,
            display_name: $("auth-name").value,
          }),
        });
        setAuth(auth);
      } catch (error) { showAuthError(error); }
    });

    $("login-btn").addEventListener("click", async () => {
      try {
        const auth = await api("/auth/login", {
          method: "POST",
          body: JSON.stringify({ email: $("auth-email").value, password: $("auth-password").value }),
        });
        setAuth(auth);
      } catch (error) { showAuthError(error); }
    });

    $("logout-btn").addEventListener("click", () => {
      localStorage.clear();
      state.token = null;
      state.user = null;
      renderShell();
    });

    $("create-collection-btn").addEventListener("click", async () => {
      try {
        const collection = await api("/collections", {
          method: "POST",
          body: JSON.stringify({
            name: $("collection-name").value,
            description: $("collection-description").value,
          }),
        });
        state.selectedCollectionId = collection.id;
        localStorage.setItem("kb_collection", collection.id);
        await refreshAll();
      } catch (error) { showAppError(error); }
    });

    $("ingest-doc-btn").addEventListener("click", async () => {
      if (!state.selectedCollectionId) return showAppError(new Error("Select a collection first."));
      try {
        await api(`/collections/${state.selectedCollectionId}/documents`, {
          method: "POST",
          body: JSON.stringify({ source: $("document-source").value, text: $("document-text").value }),
        });
        await refreshAll();
      } catch (error) { showAppError(error); }
    });

    $("new-chat-btn").addEventListener("click", () => {
      state.sessionId = null;
      localStorage.removeItem("kb_session");
      $("chat-log").innerHTML = "";
    });

    $("ask-btn").addEventListener("click", async () => {
      if (!state.selectedCollectionId) return showAppError(new Error("Select a collection first."));
      const question = $("chat-question").value;
      addBubble("user", question);
      try {
        const data = await api(`/collections/${state.selectedCollectionId}/chat`, {
          method: "POST",
          body: JSON.stringify({ question, session_id: state.sessionId, top_k: 4 }),
        });
        state.sessionId = data.session_id;
        localStorage.setItem("kb_session", data.session_id);
        addBubble("assistant", `${data.answer}\\n\\nCitations: ${data.citations.length}`);
        await loadMetrics();
      } catch (error) {
        addBubble("assistant", error.message || String(error));
      }
    });

    renderShell();
    refreshAll().catch(showAppError);
  </script>
</body>
</html>
        """
    )
