let currentSessionId = null;

const chatWindow = document.getElementById("chatWindow");
const sessionStatus = document.getElementById("sessionStatus");
const sessionMetric = document.getElementById("sessionMetric");
const ticketMetric = document.getElementById("ticketMetric");
const newSessionBtn = document.getElementById("newSessionBtn");
const chatForm = document.getElementById("chatForm");
const queryInput = document.getElementById("queryInput");
const ticketsList = document.getElementById("ticketsList");
const refreshTicketsBtn = document.getElementById("refreshTicketsBtn");
const voiceForm = document.getElementById("voiceForm");
const audioInput = document.getElementById("audioInput");
const voiceResult = document.getElementById("voiceResult");

function clearWelcomeCard() {
  const welcome = chatWindow.querySelector(".welcome-card");
  if (welcome) welcome.remove();
}

function appendMessage(role, content, metadata = {}) {
  clearWelcomeCard();

  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  const text = document.createElement("div");
  text.textContent = content;
  bubble.appendChild(text);

  if (role === "assistant" && metadata.confidence !== undefined) {
    const meta = document.createElement("div");
    meta.className = "meta";
    const confidencePercent = Math.round(metadata.confidence * 100);
    meta.textContent = `Confidence ${confidencePercent}%`;
    bubble.appendChild(meta);
  }

  if (role === "assistant" && metadata.escalate !== undefined) {
    const badge = document.createElement("span");
    badge.className = metadata.escalate ? "badge danger" : "badge success";
    badge.textContent = metadata.escalate
      ? `Support review needed${metadata.ticketId ? ` · Ticket #${metadata.ticketId}` : ""}`
      : "Resolved with support guidance";
    bubble.appendChild(badge);
  }

  wrapper.appendChild(bubble);
  chatWindow.appendChild(wrapper);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function startSession() {
  const response = await fetch("/chat/start", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({user_label: "web-demo"}),
  });

  if (!response.ok) {
    alert("Failed to start session");
    return;
  }

  const data = await response.json();
  currentSessionId = data.session_id;

  sessionStatus.textContent = `Session #${currentSessionId} is open`;
  sessionMetric.textContent = `#${currentSessionId}`;

  chatWindow.innerHTML = "";
  appendMessage(
    "assistant",
    "Hi, I’m your support assistant. Tell me what happened and I’ll help you with the next step."
  );
}

async function sendMessage(query) {
  if (!currentSessionId) {
    await startSession();
  }

  appendMessage("user", query);

  const response = await fetch(`/chat/${currentSessionId}/message`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({query}),
  });

  if (!response.ok) {
    appendMessage("assistant", "Sorry, something went wrong while processing your message.");
    return;
  }

  const data = await response.json();

  appendMessage("assistant", data.answer, {
    confidence: data.confidence,
    escalate: data.escalate,
    ticketId: data.ticket_id,
  });

  if (data.escalate) {
    await loadTickets();
  }
}

async function loadTickets() {
  const response = await fetch("/tickets");

  if (!response.ok) {
    ticketsList.innerHTML = "<p class='muted'>Failed to load tickets.</p>";
    return;
  }

  const tickets = await response.json();
  ticketMetric.textContent = `${tickets.length} open`;

  if (tickets.length === 0) {
    ticketsList.innerHTML = "<p class='muted'>No escalated issues yet.</p>";
    return;
  }

  ticketsList.innerHTML = "";

  for (const ticket of tickets.slice(0, 6)) {
    const item = document.createElement("div");
    item.className = "ticket";
    item.innerHTML = `
      <strong>#${ticket.id} · ${formatIssueType(ticket.issue_type)}</strong>
      <p>Session ${ticket.session_id} · ${ticket.status}</p>
      <p>${ticket.summary}</p>
    `;
    ticketsList.appendChild(item);
  }
}

function formatIssueType(issueType) {
  return issueType
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

async function runVoiceAsk(file) {
  const formData = new FormData();
  formData.append("file", file);

  voiceResult.innerHTML = `
    <div class="voice-result-card">
      <span class="label">Processing</span>
      <p>Transcribing audio and preparing a support response...</p>
    </div>
  `;

  const response = await fetch("/voice-ask", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    voiceResult.innerHTML = `
      <div class="voice-result-card">
        <span class="label">Error</span>
        <p>Voice request failed. Try a shorter audio file.</p>
      </div>
    `;
    return;
  }

  const data = await response.json();

  voiceResult.innerHTML = `
    <div class="voice-result-card">
      <div class="voice-section">
        <span class="label">Transcript</span>
        <p>${data.transcript || "No transcript returned."}</p>
      </div>

      <div class="voice-section">
        <span class="label">Support response</span>
        <p>${data.answer}</p>
      </div>

      <span class="${data.escalate ? "badge danger" : "badge success"}">
        ${data.escalate ? "Support review needed" : "Resolved with support guidance"}
      </span>
    </div>
  `;
}

newSessionBtn.addEventListener("click", startSession);
refreshTicketsBtn.addEventListener("click", loadTickets);

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const query = queryInput.value.trim();
  if (!query) return;

  queryInput.value = "";
  await sendMessage(query);
});

document.querySelectorAll(".quick-chip").forEach((button) => {
  button.addEventListener("click", async () => {
    const query = button.dataset.query;
    await sendMessage(query);
  });
});

voiceForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const file = audioInput.files[0];
  if (!file) {
    alert("Choose an audio file first.");
    return;
  }

  await runVoiceAsk(file);
});

loadTickets();