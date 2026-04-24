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
const kbForm = document.getElementById("kbForm");
const kbInput = document.getElementById("kbInput");
const kbList = document.getElementById("kbList");
const kbCount = document.getElementById("kbCount");
const refreshKbBtn = document.getElementById("refreshKbBtn");
const reindexKbBtn = document.getElementById("reindexKbBtn");

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

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

async function loadKBDocuments() {
  const response = await fetch("/kb/documents");

  if (!response.ok) {
    kbList.innerHTML = "<p class='muted'>Failed to load knowledge-base documents.</p>";
    return;
  }

  const docs = await response.json();
  kbCount.textContent = `${docs.length} docs`;

  if (docs.length === 0) {
    kbList.innerHTML = "<p class='muted'>No knowledge-base documents yet.</p>";
    return;
  }

  kbList.innerHTML = "";

  for (const doc of docs) {
    const item = document.createElement("div");
    item.className = "kb-doc";

    const canDelete = doc.source_type === "uploaded" && doc.id !== null;

    item.innerHTML = `
      <span class="kb-source-badge ${doc.source_type}">
        ${doc.source_type}
      </span>
      <strong>${doc.filename}</strong>
      <div class="kb-doc-meta">
        <span>${formatBytes(doc.size_bytes)}</span>
        ${doc.created_at ? `<span>${new Date(doc.created_at).toLocaleString()}</span>` : ""}
      </div>
      ${
        canDelete
          ? `<button class="delete-doc-button" data-doc-id="${doc.id}">Delete</button>`
          : ""
      }
    `;

    kbList.appendChild(item);
  }

  document.querySelectorAll(".delete-doc-button").forEach((button) => {
    button.addEventListener("click", async () => {
      const docId = button.dataset.docId;
      await deleteKBDocument(docId);
    });
  });
}

async function uploadKBDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  kbList.innerHTML = "<p class='muted'>Uploading document...</p>";

  const response = await fetch("/kb/upload", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    kbList.innerHTML = `<p class='muted'>Upload failed: ${error.detail || "unknown error"}</p>`;
    return;
  }

  await loadKBDocuments();
}

async function deleteKBDocument(docId) {
  const confirmed = window.confirm("Delete this uploaded knowledge-base document?");
  if (!confirmed) return;

  const response = await fetch(`/kb/documents/${docId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    alert("Failed to delete document.");
    return;
  }

  await loadKBDocuments();
}

async function reindexKnowledgeBase() {
  kbList.innerHTML = "<p class='muted'>Reindexing knowledge base...</p>";

  const response = await fetch("/kb/reindex", {
    method: "POST",
  });

  if (!response.ok) {
    kbList.innerHTML = "<p class='muted'>Reindex failed.</p>";
    return;
  }

  const data = await response.json();
  await loadKBDocuments();

  const notice = document.createElement("div");
  notice.className = "kb-doc";
  notice.innerHTML = `
    <span class="kb-source-badge uploaded">reindexed</span>
    <strong>${data.document_count} documents · ${data.chunk_count} chunks</strong>
    <div class="kb-doc-meta">
      <span>${data.message}</span>
    </div>
  `;

  kbList.prepend(notice);
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

kbForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const file = kbInput.files[0];
  if (!file) {
    alert("Choose a .md or .txt file first.");
    return;
  }

  await uploadKBDocument(file);
  kbInput.value = "";
});

refreshKbBtn.addEventListener("click", loadKBDocuments);
reindexKbBtn.addEventListener("click", reindexKnowledgeBase);

loadTickets();
loadKBDocuments();