
const API_URL = "http://127.0.0.1:8000";
let currentConversation = null;

window.onload = async () => {
  await loadConversationList();
  if (!currentConversation && document.getElementById("conversationList").options.length > 0) {
    currentConversation = document.getElementById("conversationList").value;
  }
  loadHistory();
};

async function loadConversationList() {
  const res = await fetch(`${API_URL}/list_conversations/`);
  const data = await res.json();

  const select = document.getElementById("conversationList");
  select.innerHTML = "";

  data.conversations.forEach(file => {
    const option = document.createElement("option");
    option.value = file;
    option.textContent = file;
    if (file === currentConversation) option.selected = true;
    select.appendChild(option);
  });

  if (!currentConversation && data.conversations.length > 0) {
    currentConversation = data.conversations[data.conversations.length - 1];
  }
}

async function loadSelectedConversation() {
  const select = document.getElementById("conversationList");
  currentConversation = select.value;
  loadHistory();
}

async function loadHistory() {
  if (!currentConversation) return;

  const res = await fetch(`${API_URL}/history/?conversation=${currentConversation}`);
  const data = await res.json();

  const chatBox = document.getElementById("chatBox");
  chatBox.innerHTML = "";

  data.history.split("\n").forEach(line => {
    if (!line.trim()) return;
    let sender = "Sistema";
    if (line.startsWith("Usuario:")) sender = "Tú";
    else if (line.startsWith("Bot:")) sender = "Bot";
    const text = line.replace(/^(Usuario|Bot|Sistema): /, "");
    addMessage(sender, text);
  });
}

async function newConversation() {
  const res = await fetch(`${API_URL}/new_conversation/`, { method: "POST" });
  const data = await res.json();

  currentConversation = data.file;
  await loadConversationList();
  loadHistory();
}

async function clearHistory() {
  if (!currentConversation) return;
  const formData = new FormData();
  formData.append("conversation", currentConversation);
  await fetch(`${API_URL}/clear/`, { method: "POST", body: formData });
  loadHistory();
}

async function uploadFile() {
  if (!currentConversation) return alert("Primero crea o selecciona una conversación");
  const file = document.getElementById("fileInput").files[0];
  if (!file) return alert("Selecciona un archivo primero");

  const formData = new FormData();
  formData.append("file", file);
  formData.append("conversation", currentConversation);

  await fetch(`${API_URL}/upload/`, { method: "POST", body: formData });
  loadHistory();
}

async function sendMessage() {
  if (!currentConversation) return alert("Primero crea o selecciona una conversación");

  const input = document.getElementById("userInput");
  const message = input.value.trim();
  if (!message) return;

  addMessage("Tú", message);
  input.value = "";

  const formData = new FormData();
  formData.append("message", message);
  formData.append("conversation", currentConversation);

  const res = await fetch(`${API_URL}/chat/`, { method: "POST", body: formData });
  const data = await res.json();

  addMessage("Bot", data.response);
  loadHistory();
}

function addMessage(sender, text) {
  const chatBox = document.getElementById("chatBox");
  const msg = document.createElement("p");
  msg.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}
