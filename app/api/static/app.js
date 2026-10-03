const API_URL = "/api/ask";
const messagesEl = document.getElementById("messages");
const questionEl = document.getElementById("question");
const sendBtn = document.getElementById("sendBtn");
const sourcesEl = document.getElementById("sources");
const latencyEl = document.getElementById("metric-latency");
const agentEl = document.getElementById("metric-agent");

function nowTime() {
  return new Date().toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
}

function addMessage(text, role) {
  const row = document.createElement("div");
  row.className = "flex gap-3" + (role === "user" ? " flex-row-reverse" : "");

  const avatar = document.createElement("div");
  avatar.className = role === "user"
    ? "w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-sm flex-shrink-0"
    : "w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm flex-shrink-0";
  avatar.textContent = role === "user" ? "👤" : "🤖";

  const bubble = document.createElement("div");
  bubble.className = role === "user"
    ? "bg-blue-600 rounded-2xl rounded-tr-sm px-4 py-3 max-w-2xl"
    : "bg-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 max-w-2xl";
  bubble.innerHTML = `<p class="text-sm leading-relaxed whitespace-pre-wrap">${escapeHtml(text)}</p>
                      <p class="text-xs text-slate-500 mt-1.5">${nowTime()}</p>`;

  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return row;
}

function addTyping() {
  const row = document.createElement("div");
  row.id = "typingRow";
  row.className = "flex gap-3";
  row.innerHTML = `
    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm flex-shrink-0">🤖</div>
    <div class="bg-slate-800 rounded-2xl rounded-tl-sm px-4 py-3">
      <div class="flex gap-1">
        <span class="w-2 h-2 bg-slate-500 rounded-full animate-bounce"></span>
        <span class="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style="animation-delay: 0.15s"></span>
        <span class="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style="animation-delay: 0.3s"></span>
      </div>
      <p class="text-xs text-slate-500 mt-2">Qwen думает... обычно 5-15 сек</p>
    </div>`;
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function removeTyping() {
  document.getElementById("typingRow")?.remove();
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function renderSources(sources) {
  sourcesEl.innerHTML = "";
  if (!sources || sources.length === 0) {
    sourcesEl.innerHTML = `<p class="text-sm text-slate-500 italic">Источники не найдены.</p>`;
    return;
  }
  sources.forEach((src, i) => {
    const el = document.createElement("div");
    el.className = "bg-slate-900 rounded-lg p-3 border border-slate-700 text-sm";
    el.innerHTML = `
      <div class="flex items-center gap-2">
        <span class="w-6 h-6 rounded bg-blue-900 text-blue-300 flex items-center justify-center text-xs font-semibold">${i + 1}</span>
        <span class="text-slate-200">${escapeHtml(src)}</span>
      </div>`;
    sourcesEl.appendChild(el);
  });
}

async function sendQuestion() {
  const text = questionEl.value.trim();
  if (!text) return;

  questionEl.value = "";
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
    latencyEl.textContent = `${(data.latency_ms / 1000).toFixed(1)} s`;
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
  messagesEl.innerHTML = `
    <div class="flex gap-3">
      <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm flex-shrink-0">🤖</div>
      <div class="bg-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 max-w-2xl">
        <p class="text-sm">Чат очищен. Задайте новый вопрос.</p>
      </div>
    </div>`;
  sourcesEl.innerHTML = `<p class="text-sm text-slate-500 italic">Задайте вопрос — здесь появятся документы.</p>`;
  latencyEl.textContent = "—";
  agentEl.textContent = "—";
}