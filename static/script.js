const messagesEl = document.getElementById("messages");
const form = document.getElementById("composer");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const chipsEl = document.getElementById("chips");
const newBtn = document.getElementById("newBtn");

const BOT_ICON = `<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="8" width="16" height="11" rx="3"/><path d="M12 4v4"/><circle cx="12" cy="3.5" r="1" fill="#ffe500" stroke="none"/><circle cx="9" cy="13" r="1" fill="#ffe500" stroke="none"/><circle cx="15" cy="13" r="1" fill="#ffe500" stroke="none"/></svg>`;
const SUGGESTIONS = ["Best phone under ₹20,000", "Noise-cancelling headphones", "Laptop for coding under ₹60,000"];
const STAGES = ["Searching the web for options…", "Reading reviews and specs…", "Comparing and picking the best…"];

let mode = "research"; // "research" first, then "chat" for follow-ups
let busy = false;

/* ---------- tiny, safe markdown renderer ---------- */
const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
function inline(s) {
  return esc(s)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*\s][^*]*)\*/g, "$1<em>$2</em>")
    .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/(^|[\s(])(https?:\/\/[^\s<)]+)/g, '$1<a href="$2" target="_blank" rel="noopener">$2</a>');
}
const splitRow = r => r.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map(c => c.trim());
const isSep = r => /^\s*\|[\s|:-]*-[\s|:-]*$/.test(r);
const isBlock = l => /^([-*•|#]|\d+[.)]\s)/.test(l);

function table(rows) {
  const data = rows.filter(r => !isSep(r)).map(splitRow);
  const [head, ...body] = data;
  const th = head.map(c => `<th>${inline(c)}</th>`).join("");
  const tr = body.map(r => `<tr>${r.map(c => `<td>${inline(c)}</td>`).join("")}</tr>`).join("");
  return `<div class="table-wrap"><table><thead><tr>${th}</tr></thead><tbody>${tr}</tbody></table></div>`;
}

function render(md) {
  const lines = md.replace(/\r/g, "").split("\n");
  const out = []; let list = null;
  const close = () => { if (list) { out.push(`</${list}>`); list = null; } };
  const hasMore = from => lines.slice(from).some(l => l.trim());

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    let m;
    if (!line) continue;

    if (line.startsWith("|")) {
      close();
      const rows = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) rows.push(lines[i++]);
      i--;
      out.push(table(rows));
    } else if ((m = line.match(/^#{1,4}\s+(.*)/))) {
      close(); out.push(`<h3>${inline(m[1])}</h3>`);
    } else if ((m = line.match(/^[-*•]\s+(.*)/))) {
      if (list !== "ul") { close(); out.push("<ul>"); list = "ul"; }
      out.push(`<li>${inline(m[1])}</li>`);
    } else if ((m = line.match(/^\d+[.)]\s+(.*)/))) {
      if (list !== "ol") { close(); out.push("<ol>"); list = "ol"; }
      out.push(`<li>${inline(m[1])}</li>`);
    } else if (line.length <= 80 && !/[.:,;?!]$/.test(line) && !isBlock(line) && hasMore(i + 1)) {
      close(); out.push(`<h3>${inline(line)}</h3>`);   // short standalone line = section title
    } else {
      close(); out.push(`<p>${inline(line)}</p>`);
    }
  }
  close();
  return out.join("");
}

/* ---------- UI helpers ---------- */
function scrollDown() { messagesEl.scrollTop = messagesEl.scrollHeight; }

function addMessage(role, html, isError = false) {
  const row = document.createElement("div");
  row.className = `row ${role}`;
  const wide = html.includes("<table") ? " wide" : "";
  const bubble = `<div class="bubble${wide}${isError ? " error" : ""}">${html}</div>`;
  row.innerHTML = role === "agent" ? `<div class="avatar">${BOT_ICON}</div>${bubble}` : bubble;
  messagesEl.appendChild(row);
  scrollDown();
  return row;
}

function showTyping(text) {
  return addMessage("agent", `<div class="typing"><span class="dots"><i></i><i></i><i></i></span><span class="label">${text}</span></div>`);
}

function setBusy(state) {
  busy = state;
  input.disabled = sendBtn.disabled = state;
  if (!state) input.focus();
}

function showChips(items) {
  chipsEl.innerHTML = "";
  items.forEach(t => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip"; b.textContent = t;
    b.onclick = () => { input.value = t; form.requestSubmit(); };
    chipsEl.appendChild(b);
  });
}

async function post(url, body) {
  const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

function greet() {
  messagesEl.innerHTML = "";
  mode = "research";
  input.placeholder = "What do you want to buy?";
  addMessage("agent", "<p>Hi, I’m <strong>BuySmart AI</strong>. Tell me what you want to buy and I’ll research the best options for you. Afterwards, ask me anything about the results.</p>");
  showChips(SUGGESTIONS);
}

/* ---------- main flow ---------- */
form.addEventListener("submit", async e => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text || busy) return;

  input.value = "";
  chipsEl.innerHTML = "";
  addMessage("user", esc(text));
  setBusy(true);

  const typing = showTyping(mode === "research" ? STAGES[0] : "Checking the research…");
  let timer;
  if (mode === "research") {
    let i = 0;
    timer = setInterval(() => {
      i = Math.min(i + 1, STAGES.length - 1);
      typing.querySelector(".label").textContent = STAGES[i];
    }, 7000);
  }

  try {
    const data = mode === "research"
      ? await post("/api/research", { query: text })
      : await post("/api/chat", { message: text });
    typing.remove();
    addMessage("agent", render(data.answer));
    if (mode === "research" && data.followups === false) {
      showChips(SUGGESTIONS);   // nothing found: stay in search mode
    } else if (mode === "research") {
      mode = "chat";
      input.placeholder = "Ask a follow-up about your research…";
      showChips(["Which one is the best value?", "Any downsides I should know?", "Compare the top two"]);
    }
  } catch (err) {
    typing.remove();
    addMessage("agent", `<p>${esc(err.message)}</p>`, true);
  } finally {
    clearInterval(timer);
    setBusy(false);
  }
});

newBtn.addEventListener("click", async () => {
  if (busy) return;
  await fetch("/api/end", { method: "POST" }).catch(() => {});
  greet();
});

// Delete research data when the tab closes
window.addEventListener("pagehide", () => navigator.sendBeacon("/api/end"));

greet();
