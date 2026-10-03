const API_URL = "/api/ask";
const messagesEl = document.getElementById("messages");
const questionEl = document.getElementById("question");
const sendBtn = document.getElementById("sendBtn");
const sourcesEl = document.getElementById("sources");
const latencyEl = document.getElementById("metric-latency");
const agentEl = document.getElementById("metric-agent");

const ICON_ASSISTANT = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>`;
const ICON_USER = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0116 0"/></svg>`;

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function hideWelcome() {
  document.getElementById("welcome")?.remove();
}

function addMessage(text, role) {
  const msg = document.createElement("div");
  msg.className = `msg ${role}`;
  msg.innerHTML = `
    <div class="avatar ${role}">${role === "user" ? ICON_USER : ICON_ASSISTANT}</div>
    <div class="bubble">${escapeHtml(text)}</div>
  `;
  messagesEl.appendChild(msg);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addTyping() {
  const msg = document.createElement("div");
  msg.className = "msg assistant";
  msg.id = "typingRow";
  msg.innerHTML = `
    <div class="avatar assistant">${ICON_ASSISTANT}</div>
    <div class="bubble">
      <div class="typing-dots"><span></span><span></span><span></span></div>
    </div>
  `;
  messagesEl.appendChild(msg);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function removeTyping() {
  document.getElementById("typingRow")?.remove();
}

function getScoreLevel(score) {
  if (score >= 0.85) return "high";
  if (score >= 0.75) return "mid";
  return "low";
}

function renderSources(sources) {
  sourcesEl.innerHTML = "";
  if (!sources || sources.length === 0) {
    sourcesEl.innerHTML = `<div class="empty">Источники не найдены</div>`;
    return;
  }
  sources.forEach((src, i) => {
    const preview = src.content.length > 100
      ? src.content.slice(0, 100).trim() + "…"
      : src.content;
    const level = getScoreLevel(src.score);

    const el = document.createElement("button");
    el.className = "src-item";
    el.onclick = () => openSourceModal(src);
    el.innerHTML = `
      <div class="src-head">
        <span class="src-num">${i + 1}</span>
        <span class="src-title">${escapeHtml(src.title)}</span>
        <span class="src-score ${level}">${src.score.toFixed(2)}</span>
      </div>
      <div class="src-preview">${escapeHtml(preview)}</div>
    `;
    sourcesEl.appendChild(el);
  });
}

function openSourceModal(src) {
  const modal = document.getElementById("sourceModal");
  document.getElementById("modalTitle").textContent = src.title;
  document.getElementById("modalScore").textContent = `score ${src.score.toFixed(3)}`;
  document.getElementById("modalBody").textContent = src.content;
  modal.classList.add("active");
}

function closeSourceModal() {
  document.getElementById("sourceModal").classList.remove("active");
}

async function sendQuestion() {
  const text = questionEl.value.trim();
  if (!text) return;

  hideWelcome();
  questionEl.value = "";
  autoGrow(questionEl);
  sendBtn.disabled = true;
  addMessage(text, "user");
  addTyping();

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: text }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    removeTyping();
    addMessage(data.answer, "assistant");
    renderSources(data.sources);
    latencyEl.textContent = `${(data.latency_ms / 1000).toFixed(1)}s`;
    agentEl.textContent = data.agent;
  } catch (e) {
    removeTyping();
    addMessage(`Ошибка: ${e.message}`, "assistant");
  } finally {
    sendBtn.disabled = false;
    questionEl.focus();
  }
}

function askQuick(text) {
  questionEl.value = text;
  sendQuestion();
}

function clearChat() {
  messagesEl.innerHTML = "";
  messagesEl.appendChild(buildWelcome());
  sourcesEl.innerHTML = `<div class="empty">Появятся после ответа</div>`;
  latencyEl.textContent = "—";
  agentEl.textContent = "—";
}

function buildWelcome() {
  const welcome = document.createElement("div");
  welcome.id = "welcome";
  welcome.className = "welcome";
  welcome.innerHTML = `
    <div class="welcome-mark">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>
      </svg>
    </div>
    <h1 class="welcome-title">Чем помочь клиенту?</h1>
    <p class="welcome-sub">Задайте вопрос или выберите готовый сценарий</p>
    <div class="welcome-grid">
      <button class="welcome-tile" onclick="askQuick('Сколько стоит доставка в Москву?')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>
        <span>Сколько стоит доставка?</span>
      </button>
      <button class="welcome-tile" onclick="askQuick('Как вернуть товар?')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 102.13-9.36L1 10"/></svg>
        <span>Как вернуть товар?</span>
      </button>
      <button class="welcome-tile" onclick="askQuick('Какие есть наушники?')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 18v-6a9 9 0 0118 0v6"/><path d="M21 19a2 2 0 01-2 2h-1a2 2 0 01-2-2v-3a2 2 0 012-2h3zM3 19a2 2 0 002 2h1a2 2 0 002-2v-3a2 2 0 00-2-2H3z"/></svg>
        <span>Что есть из наушников?</span>
      </button>
      <button class="welcome-tile" onclick="askQuick('Можно оплатить картой?')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>
        <span>Способы оплаты?</span>
      </button>
    </div>
  `;
  return welcome;
}

function handleKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendQuestion();
  }
}

function autoGrow(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 160) + "px";
}

// Закрытие модалки по Escape
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeSourceModal();
});