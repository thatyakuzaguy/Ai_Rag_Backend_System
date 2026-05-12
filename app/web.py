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
      color-scheme: light;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f6f7f9;
      color: #15171a;
    }
    * { box-sizing: border-box; }
    body { margin: 0; }
    main {
      width: min(1160px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }
    header {
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 16px;
      padding: 8px 0 24px;
      border-bottom: 1px solid #d9dde4;
    }
    h1 { margin: 0; font-size: clamp(28px, 5vw, 44px); line-height: 1.05; }
    .subtle { color: #5b6472; margin: 8px 0 0; }
    .docs {
      color: #0f5c6e;
      text-decoration: none;
      font-weight: 700;
      white-space: nowrap;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
      margin-top: 22px;
    }
    section {
      background: #ffffff;
      border: 1px solid #dfe3ea;
      border-radius: 8px;
      padding: 18px;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
    }
    section.wide { grid-column: 1 / -1; }
    h2 { margin: 0 0 14px; font-size: 18px; }
    label { display: block; font-weight: 700; margin: 12px 0 6px; }
    input, textarea {
      width: 100%;
      border: 1px solid #c8ced8;
      border-radius: 6px;
      padding: 10px 12px;
      font: inherit;
      background: #fff;
      color: #15171a;
    }
    textarea { min-height: 160px; resize: vertical; }
    button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 40px;
      margin-top: 14px;
      border: 0;
      border-radius: 6px;
      padding: 0 14px;
      background: #165f72;
      color: white;
      font: inherit;
      font-weight: 800;
      cursor: pointer;
    }
    button:hover { background: #104b5b; }
    .secondary {
      margin-left: 8px;
      background: #e7ebf0;
      color: #24303d;
    }
    .secondary:hover { background: #d7dde6; }
    pre {
      min-height: 120px;
      overflow: auto;
      margin: 14px 0 0;
      padding: 12px;
      border-radius: 6px;
      background: #101418;
      color: #e9f1f7;
      white-space: pre-wrap;
      word-break: break-word;
    }
    .output {
      min-height: 120px;
      margin: 14px 0 0;
      padding: 12px;
      border-radius: 6px;
      background: #f8fafc;
      border: 1px solid #dfe3ea;
    }
    .result {
      padding: 12px 0;
      border-top: 1px solid #e2e6ed;
    }
    .result:first-child { border-top: 0; padding-top: 0; }
    .result strong { display: block; margin-bottom: 4px; }
    .score { color: #5b6472; font-size: 13px; }
    .answer {
      margin: 0 0 12px;
      font-size: 17px;
      line-height: 1.55;
    }
    .empty { color: #687386; }
    .status {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin-top: 10px;
      color: #45505f;
      font-size: 14px;
    }
    .dot {
      width: 10px;
      height: 10px;
      border-radius: 999px;
      background: #b6bdc9;
    }
    .dot.ok { background: #2f8f5b; }
    @media (max-width: 820px) {
      header { align-items: start; flex-direction: column; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>AI RAG Backend System</h1>
        <p class="subtle">Ingest documents, search context, and ask grounded questions.</p>
        <span class="status"><span id="health-dot" class="dot"></span><span id="health-text">Checking API</span></span>
      </div>
      <a class="docs" href="/docs">Open API Docs</a>
    </header>

    <div class="grid">
      <section>
        <h2>Ingest Document</h2>
        <label for="source">Source</label>
        <input id="source" value="portfolio-demo" />
        <label for="document-text">Text</label>
        <textarea id="document-text">RAG retrieves relevant context before generating a grounded answer with citations.</textarea>
        <button id="ingest-btn">Ingest</button>
        <div id="ingest-output" class="output"></div>
      </section>

      <section>
        <h2>Search</h2>
        <label for="search-query">Query</label>
        <input id="search-query" value="grounded answer with citations" />
        <label for="search-top-k">Top K</label>
        <input id="search-top-k" type="number" min="1" max="20" value="3" />
        <button id="search-btn">Search</button>
        <div id="search-output" class="output"></div>
      </section>

      <section class="wide">
        <h2>Chat</h2>
        <label for="question">Question</label>
        <input id="question" value="What does RAG retrieve before answering?" />
        <label for="chat-top-k">Top K</label>
        <input id="chat-top-k" type="number" min="1" max="20" value="3" />
        <button id="chat-btn">Ask</button>
        <button id="clear-chat-btn" class="secondary">Clear Chat Context</button>
        <div id="chat-output" class="output"></div>
      </section>
    </div>
  </main>

  <script>
    const $ = (id) => document.getElementById(id);
    const conversationHistory = [];

    async function request(path, options = {}) {
      const response = await fetch(path, {
        headers: { "Content-Type": "application/json", ...(options.headers || {}) },
        ...options,
      });
      const text = await response.text();
      let body;
      try { body = JSON.parse(text); } catch { body = text; }
      if (!response.ok) throw { status: response.status, body };
      return body;
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function showJson(id, value) {
      $(id).innerHTML = `<pre>${escapeHtml(JSON.stringify(value, null, 2))}</pre>`;
    }

    function showError(id, error) {
      showJson(id, { error: error.status || "request_failed", detail: error.body || String(error) });
    }

    function showIngest(data) {
      $("ingest-output").innerHTML = `
        <strong>Indexed ${data.chunks_indexed} chunk${data.chunks_indexed === 1 ? "" : "s"}</strong>
        <p class="subtle">Source: ${escapeHtml(data.source)}</p>
      `;
    }

    function showSearch(data) {
      if (!data.results.length) {
        $("search-output").innerHTML = `<p class="empty">No matching chunks found. Ingest a document first.</p>`;
        return;
      }
      $("search-output").innerHTML = data.results.map((item, index) => `
        <div class="result">
          <strong>${index + 1}. ${escapeHtml(item.source)}</strong>
          <div class="score">Score: ${Number(item.score).toFixed(3)} | Chunk: ${escapeHtml(item.id)}</div>
          <p>${escapeHtml(item.text)}</p>
        </div>
      `).join("");
    }

    function showChat(data) {
      const citations = data.citations.map((item) => `
        <div class="score">${escapeHtml(item.source)} | ${escapeHtml(item.chunk_id)} | score ${Number(item.score).toFixed(3)}</div>
      `).join("");
      const historyNote = conversationHistory.length
        ? `<div class="score">Using ${conversationHistory.length} previous chat message${conversationHistory.length === 1 ? "" : "s"} as conversation context.</div>`
        : `<div class="score">No previous chat context used.</div>`;
      $("chat-output").innerHTML = `
        <p class="answer">${escapeHtml(data.answer)}</p>
        ${historyNote}
        <strong>Citations</strong>
        ${citations || `<p class="empty">No citations returned.</p>`}
      `;
    }

    async function checkHealth() {
      try {
        const data = await request("/health");
        $("health-dot").classList.add("ok");
        $("health-text").textContent = `API online: ${data.documents} documents, ${data.chunks_indexed} chunks`;
      } catch {
        $("health-text").textContent = "API unavailable";
      }
    }

    $("ingest-btn").addEventListener("click", async () => {
      try {
        const data = await request("/documents", {
          method: "POST",
          body: JSON.stringify({
            source: $("source").value,
            text: $("document-text").value,
            metadata: { ui: "home" },
          }),
        });
        showIngest(data);
        checkHealth();
      } catch (error) {
        showError("ingest-output", error);
      }
    });

    $("search-btn").addEventListener("click", async () => {
      try {
        const params = new URLSearchParams({
          query: $("search-query").value,
          top_k: $("search-top-k").value,
        });
        showSearch(await request(`/search?${params}`));
      } catch (error) {
        showError("search-output", error);
      }
    });

    $("chat-btn").addEventListener("click", async () => {
      try {
        const question = $("question").value;
        const data = await request("/chat", {
          method: "POST",
          body: JSON.stringify({
            question,
            top_k: Number($("chat-top-k").value),
            history: conversationHistory.slice(-10),
          }),
        });
        showChat(data);
        conversationHistory.push({ role: "user", content: question });
        conversationHistory.push({ role: "assistant", content: data.answer });
      } catch (error) {
        showError("chat-output", error);
      }
    });

    $("clear-chat-btn").addEventListener("click", () => {
      conversationHistory.length = 0;
      $("chat-output").innerHTML = `<p class="empty">Chat context cleared.</p>`;
    });

    checkHealth();
  </script>
</body>
</html>
        """
    )
