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
      --bg: #fff8f8;
      --panel: rgba(255, 255, 255, 0.92);
      --panel-solid: #ffffff;
      --ink: #22191d;
      --muted: #7a6670;
      --line: #ead5dc;
      --brand: #b84f74;
      --brand-dark: #8f3457;
      --soft: #fff0f4;
      --sidebar: #2a2027;
      --sidebar-soft: #3a2933;
      --danger: #b42318;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        linear-gradient(135deg, rgba(255, 245, 247, 0.92), rgba(255, 252, 248, 0.96)),
        var(--bg);
    }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; }
    button, input, textarea { font: inherit; }
    button {
      min-height: 40px;
      border: 0;
      border-radius: 8px;
      padding: 0 14px;
      background: var(--brand);
      color: #fff;
      font-weight: 800;
      cursor: pointer;
    }
    button:hover { background: var(--brand-dark); }
    button.secondary { background: #f3e6eb; color: #3d2933; }
    button.secondary:hover { background: #ead5dc; }
    input, textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 11px 12px;
      background: #fffdfd;
      color: var(--ink);
      outline-color: #d97898;
    }
    textarea { min-height: 150px; resize: vertical; }
    label { display: block; margin: 12px 0 6px; font-size: 13px; font-weight: 800; color: #5f4350; }
    .hidden { display: none !important; }
    .muted { color: var(--muted); }
    .error { color: var(--danger); }
    .petals {
      position: fixed;
      inset: 0;
      pointer-events: none;
      overflow: hidden;
      z-index: 0;
    }
    .petal {
      position: absolute;
      width: 15px;
      height: 22px;
      border-radius: 70% 30% 70% 30%;
      background: rgba(232, 135, 164, 0.24);
      transform: rotate(28deg);
    }
    .petal:nth-child(1) { left: 8%; top: 12%; }
    .petal:nth-child(2) { left: 72%; top: 10%; transform: rotate(-18deg); }
    .petal:nth-child(3) { left: 87%; top: 48%; }
    .petal:nth-child(4) { left: 18%; top: 78%; transform: rotate(-38deg); }
    .petal:nth-child(5) { left: 54%; top: 86%; }
    .auth {
      position: relative;
      z-index: 1;
      max-width: 1080px;
      margin: 44px auto;
      display: grid;
      grid-template-columns: 1fr 430px;
      gap: 24px;
      padding: 0 20px;
    }
    .auth-hero {
      min-height: 500px;
      padding: 34px;
      border-radius: 14px;
      background:
        linear-gradient(135deg, rgba(42, 32, 39, 0.94), rgba(91, 50, 66, 0.9));
      color: #fff7fa;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 0 24px 70px rgba(91, 50, 66, 0.18);
    }
    .brand { font-size: 22px; font-weight: 950; letter-spacing: 0; }
    .auth-hero h1 { margin: 18px 0 12px; font-size: clamp(40px, 6vw, 64px); line-height: 0.98; }
    .tagline { color: #f4dce5; line-height: 1.55; max-width: 620px; }
    .auth-card, .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 22px;
      box-shadow: 0 18px 45px rgba(90, 48, 64, 0.08);
      backdrop-filter: blur(10px);
    }
    .app {
      position: relative;
      z-index: 1;
      display: grid;
      grid-template-columns: 288px minmax(0, 1fr);
      min-height: 100vh;
    }
    aside {
      background:
        linear-gradient(180deg, rgba(42, 32, 39, 0.98), rgba(52, 37, 47, 0.98));
      color: #fff7fa;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .new-chat {
      width: 100%;
      background: #fff7fa;
      color: #3a2933;
    }
    nav { display: grid; gap: 8px; }
    .nav-btn {
      width: 100%;
      text-align: left;
      background: transparent;
      border: 1px solid rgba(255,255,255,0.1);
      color: #f7e8ee;
    }
    .nav-btn.active, .nav-btn:hover { background: var(--sidebar-soft); }
    .sidebar-footer {
      margin-top: auto;
      display: grid;
      gap: 8px;
      color: #dec4ce;
      font-size: 13px;
    }
    main {
      display: grid;
      grid-template-rows: auto 1fr;
      min-width: 0;
    }
    .topbar {
      height: 72px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 0 24px;
      border-bottom: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.72);
      backdrop-filter: blur(10px);
    }
    .page { padding: 24px; min-width: 0; }
    h1, h2, h3 { margin: 0; }
    h1 { font-size: 26px; }
    h2 { font-size: 20px; margin-bottom: 14px; }
    h3 { font-size: 15px; margin-bottom: 6px; }
    .grid { display: grid; gap: 16px; }
    .cols-2 { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); }
    .cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
    .metric strong { display: block; font-size: 30px; }
    .metric span { color: var(--muted); font-size: 13px; }
    .item {
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 13px;
      background: #fffdfd;
    }
    .item.active { border-color: var(--brand); background: var(--soft); }
    .toolbar { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .chat-page {
      height: calc(100vh - 72px);
      display: grid;
      grid-template-rows: 1fr auto;
      padding: 0;
    }
    .chat-log {
      overflow: auto;
      padding: 28px max(24px, 12vw);
      display: grid;
      align-content: start;
      gap: 16px;
    }
    .empty-chat {
      align-self: center;
      justify-self: center;
      text-align: center;
      max-width: 620px;
      padding: 30px;
    }
    .empty-chat h2 { font-size: 36px; margin-bottom: 10px; }
    .bubble {
      max-width: 760px;
      padding: 14px 16px;
      border-radius: 14px;
      line-height: 1.55;
      white-space: pre-wrap;
      box-shadow: 0 8px 22px rgba(74, 38, 53, 0.06);
    }
    .bubble.user { justify-self: end; background: var(--brand); color: white; border-bottom-right-radius: 4px; }
    .bubble.assistant { justify-self: start; background: var(--panel-solid); border: 1px solid var(--line); border-bottom-left-radius: 4px; }
    .composer {
      padding: 18px max(24px, 12vw) 24px;
      background: linear-gradient(180deg, rgba(255,248,248,0.2), rgba(255,248,248,0.96));
    }
    .composer-box {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: white;
      box-shadow: 0 18px 40px rgba(74, 38, 53, 0.08);
    }
    .composer-box input { border: 0; }
    @media (max-width: 980px) {
      .auth, .app, .cols-2, .cols-4 { grid-template-columns: 1fr; }
      aside { min-height: auto; }
      .chat-page { height: auto; min-height: calc(100vh - 72px); }
      .chat-log, .composer { padding-left: 18px; padding-right: 18px; }
    }
  </style>
</head>
<body>
  <div class="petals">
    <span class="petal"></span><span class="petal"></span><span class="petal"></span><span class="petal"></span><span class="petal"></span>
  </div>

  <section id="auth-view" class="auth">
    <div class="auth-hero">
      <div>
        <div class="brand">KnowledgeBase AI</div>
        <h1>Sakura workspace for grounded answers.</h1>
        <p class="tagline">A ChatGPT-style RAG dashboard for private collections, document ingestion, citations, and technical learning.</p>
      </div>
      <p class="tagline">Free local AI mode by default. Optional OpenAI mode when you want richer generation.</p>
    </div>
    <div class="auth-card">
      <h2>Access workspace</h2>
      <p class="muted">Create an account or sign in. If Render redeploys, you may need to sign in again.</p>
      <label>Email</label>
      <input id="auth-email" value="demo@example.com" />
      <label>Password</label>
      <input id="auth-password" type="password" placeholder="At least 8 characters" />
      <label>Display name</label>
      <input id="auth-name" value="Demo User" />
      <div class="toolbar" style="margin-top:16px">
        <button id="demo-btn">Start guided demo</button>
        <button id="register-btn">Create account</button>
        <button id="login-btn" class="secondary">Sign in</button>
      </div>
      <p id="auth-error" class="error"></p>
    </div>
  </section>

  <section id="app-view" class="app hidden">
    <aside>
      <div>
        <div class="brand">KnowledgeBase AI</div>
        <p class="tagline">Sakura RAG workspace</p>
      </div>
      <button id="new-chat-btn" class="new-chat">New chat</button>
      <nav>
        <button class="nav-btn active" data-page="chat">Chat</button>
        <button class="nav-btn" data-page="collections">Collections</button>
        <button class="nav-btn" data-page="documents">Documents</button>
        <button class="nav-btn" data-page="settings">Settings</button>
      </nav>
      <div class="sidebar-footer">
        <span id="selected-collection-label">No collection selected</span>
        <a style="color:#fff7fa" href="/docs">API Docs</a>
        <button id="logout-btn" class="secondary">Log out</button>
      </div>
    </aside>

    <main>
      <div class="topbar">
        <div>
          <h1 id="page-title">Chat</h1>
          <p id="user-line" class="muted"></p>
        </div>
        <span id="app-error" class="error"></span>
      </div>

      <section id="page-chat" class="page chat-page">
        <div id="chat-log" class="chat-log">
          <div class="empty-chat">
            <h2>What should we explore?</h2>
            <p class="muted">You can ask right away. If no collection exists, the app will create one automatically. For best answers, add a document from the Documents page first.</p>
          </div>
        </div>
        <div class="composer">
          <div class="composer-box">
            <input id="chat-question" value="How do I prevent SQL injection in FastAPI?" />
            <button id="ask-btn">Ask</button>
          </div>
        </div>
      </section>

      <section id="page-collections" class="page hidden">
        <div class="grid cols-4" style="margin-bottom:16px">
          <div class="panel metric"><strong id="metric-collections">0</strong><span>Collections</span></div>
          <div class="panel metric"><strong id="metric-documents">0</strong><span>Documents</span></div>
          <div class="panel metric"><strong id="metric-chats">0</strong><span>Chats</span></div>
          <div class="panel metric"><strong id="metric-messages">0</strong><span>Messages</span></div>
        </div>
        <div class="grid cols-2">
          <div class="panel">
            <h2>Create collection</h2>
            <label>Name</label>
            <input id="collection-name" value="Advanced Backend Notes" />
            <label>Description</label>
            <input id="collection-description" value="Python, FastAPI, SQL, and RAG notes" />
            <button id="create-collection-btn">Create collection</button>
          </div>
          <div class="panel">
            <h2>Your collections</h2>
            <div id="collection-list" class="grid"></div>
          </div>
        </div>
      </section>

      <section id="page-documents" class="page hidden">
        <div class="grid cols-2">
          <div class="panel">
            <h2>Ingest document</h2>
            <label>Source</label>
            <input id="document-source" value="advanced-note" />
            <label>Text</label>
            <textarea id="document-text">FastAPI routes should stay thin. Use services for business logic. Prevent SQL injection with parameterized queries.</textarea>
            <button id="ingest-doc-btn">Ingest into selected collection</button>
          </div>
          <div class="panel">
            <h2>Collection documents</h2>
            <div id="doc-list" class="grid"></div>
          </div>
        </div>
      </section>

      <section id="page-settings" class="page hidden">
        <div class="panel">
          <h2>Settings</h2>
          <p class="muted">This demo stores the bearer token in browser localStorage. If Render redeploys or the database resets, sign in again.</p>
          <button id="clear-local-btn" class="secondary">Clear local browser session</button>
        </div>
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
      page: "chat",
    };
    const $ = (id) => document.getElementById(id);
    const demoDocument = [
      "This recruiter demo collection explains how the AI RAG Backend System works.",
      "The backend is built with FastAPI, Pydantic schemas, service-layer separation, and SQLite persistence.",
      "The RAG pipeline chunks documents, creates embeddings, stores vectors, retrieves similar context, and returns cited answers.",
      "SQL injection is prevented by parameterized SQLite queries instead of string-built SQL.",
      "The authenticated workspace supports collections, document ingestion, chat sessions, conversation history, and feedback.",
      "Python projects should keep route handlers thin, validate inputs, isolate business logic in services, and test important behavior with Pytest.",
    ].join("\\n");

    async function api(path, options = {}) {
      const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
      if (state.token) headers.Authorization = `Bearer ${state.token}`;
      const response = await fetch(path, { ...options, headers });
      const text = await response.text();
      let body;
      try { body = JSON.parse(text); } catch { body = text; }
      if (response.status === 401) {
        clearSession();
        throw new Error("Your session expired or the server was redeployed. Please sign in again.");
      }
      if (!response.ok) throw new Error(body.detail || body || `HTTP ${response.status}`);
      return body;
    }

    function showAppError(error) { $("app-error").textContent = error.message || String(error); }
    function showAuthError(error) { $("auth-error").textContent = error.message || String(error); }
    function clearErrors() { $("app-error").textContent = ""; $("auth-error").textContent = ""; }
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

    function clearSession() {
      localStorage.removeItem("kb_token");
      localStorage.removeItem("kb_user");
      localStorage.removeItem("kb_collection");
      localStorage.removeItem("kb_session");
      state.token = null;
      state.user = null;
      state.collections = [];
      state.selectedCollectionId = null;
      state.sessionId = null;
      renderShell();
    }

    function renderShell() {
      $("auth-view").classList.toggle("hidden", Boolean(state.token));
      $("app-view").classList.toggle("hidden", !state.token);
      if (state.user) $("user-line").textContent = `${state.user.display_name} - ${state.user.email}`;
      renderPage(state.page);
    }

    function renderPage(page) {
      state.page = page;
      const titles = { chat: "Chat", collections: "Collections", documents: "Documents", settings: "Settings" };
      $("page-title").textContent = titles[page];
      ["chat", "collections", "documents", "settings"].forEach((name) => {
        $(`page-${name}`).classList.toggle("hidden", name !== page);
      });
      document.querySelectorAll(".nav-btn").forEach((button) => {
        button.classList.toggle("active", button.dataset.page === page);
      });
    }

    async function refreshAll() {
      if (!state.token) return;
      await Promise.all([loadMetrics(), loadCollections()]);
      if (state.selectedCollectionId) await loadDocuments();
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
      if (
        state.collections.length &&
        !state.collections.some((collection) => collection.id === state.selectedCollectionId)
      ) {
        state.selectedCollectionId = state.collections[0].id;
        localStorage.setItem("kb_collection", state.selectedCollectionId);
      }
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
          await loadCollections();
          await loadDocuments();
          renderPage("chat");
        });
      });
      renderCollectionLabel();
    }

    function renderCollectionLabel() {
      const selected = state.collections.find((item) => item.id === state.selectedCollectionId);
      $("selected-collection-label").textContent = selected
        ? `Collection: ${selected.name}`
        : "No collection selected";
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

    async function ensureCollection() {
      if (state.selectedCollectionId) return state.selectedCollectionId;
      let collection = state.collections[0];
      if (!collection) {
        collection = await api("/collections", {
          method: "POST",
          body: JSON.stringify({
            name: "My Knowledge Base",
            description: "Default collection created automatically",
          }),
        });
        await loadMetrics();
      }
      state.selectedCollectionId = collection.id;
      localStorage.setItem("kb_collection", collection.id);
      await loadCollections();
      await loadDocuments();
      return collection.id;
    }

    async function startGuidedDemo() {
      const stamp = Date.now();
      const email = `reviewer-${stamp}@example.com`;
      const password = `demo-password-${stamp}`;
      $("auth-email").value = email;
      $("auth-password").value = password;
      $("auth-name").value = "Portfolio Reviewer";
      const auth = await api("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password, display_name: "Portfolio Reviewer" }),
      });
      state.token = auth.token;
      state.user = auth.user;
      localStorage.setItem("kb_token", auth.token);
      localStorage.setItem("kb_user", JSON.stringify(auth.user));
      renderShell();
      const collection = await api("/collections", {
        method: "POST",
        body: JSON.stringify({
          name: "Recruiter Demo",
          description: "Ready-to-chat sample collection for the portfolio demo",
        }),
      });
      state.selectedCollectionId = collection.id;
      localStorage.setItem("kb_collection", collection.id);
      await api(`/collections/${collection.id}/documents`, {
        method: "POST",
        body: JSON.stringify({ source: "recruiter-demo-guide", text: demoDocument }),
      });
      $("chat-question").value = "What does this project demonstrate?";
      $("chat-log").innerHTML = `
        <div class="empty-chat">
          <h2>Demo workspace ready</h2>
          <p class="muted">A sample collection has been created. Ask the suggested question or type your own.</p>
        </div>`;
      await refreshAll();
      renderPage("chat");
    }

    function addBubble(role, content) {
      const empty = document.querySelector(".empty-chat");
      if (empty) empty.remove();
      const div = document.createElement("div");
      div.className = `bubble ${role}`;
      div.textContent = content;
      $("chat-log").appendChild(div);
      $("chat-log").scrollTop = $("chat-log").scrollHeight;
    }

    $("demo-btn").addEventListener("click", async () => {
      try {
        clearErrors();
        await startGuidedDemo();
      } catch (error) { showAuthError(error); }
    });

    $("register-btn").addEventListener("click", async () => {
      try {
        clearErrors();
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
        clearErrors();
        const auth = await api("/auth/login", {
          method: "POST",
          body: JSON.stringify({ email: $("auth-email").value, password: $("auth-password").value }),
        });
        setAuth(auth);
      } catch (error) { showAuthError(error); }
    });

    $("logout-btn").addEventListener("click", clearSession);
    $("clear-local-btn").addEventListener("click", () => {
      clearSession();
      location.reload();
    });

    document.querySelectorAll(".nav-btn").forEach((button) => {
      button.addEventListener("click", () => renderPage(button.dataset.page));
    });

    $("create-collection-btn").addEventListener("click", async () => {
      try {
        clearErrors();
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
        renderPage("documents");
      } catch (error) { showAppError(error); }
    });

    $("ingest-doc-btn").addEventListener("click", async () => {
      try {
        clearErrors();
        const collectionId = await ensureCollection();
        await api(`/collections/${collectionId}/documents`, {
          method: "POST",
          body: JSON.stringify({ source: $("document-source").value, text: $("document-text").value }),
        });
        await refreshAll();
        renderPage("chat");
      } catch (error) { showAppError(error); }
    });

    $("new-chat-btn").addEventListener("click", () => {
      state.sessionId = null;
      localStorage.removeItem("kb_session");
      $("chat-log").innerHTML = `
        <div class="empty-chat">
          <h2>New chat</h2>
          <p class="muted">Ask something about your documents. A default collection will be created if needed.</p>
        </div>`;
      renderPage("chat");
    });

    $("ask-btn").addEventListener("click", async () => {
      const question = $("chat-question").value;
      addBubble("user", question);
      try {
        clearErrors();
        const collectionId = await ensureCollection();
        const data = await api(`/collections/${collectionId}/chat`, {
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
