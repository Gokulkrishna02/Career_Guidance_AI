const API = "http://127.0.0.1:8000";
const studentId = localStorage.getItem("student_id");

if (!studentId) {
  window.location.href = "login.html";
}

const messages = document.getElementById("messages");
const input = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const newChat = document.getElementById("newChat");
const logout = document.getElementById("logout");

function addMessage(text, role) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

sendBtn.onclick = async () => {
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  const typing = document.createElement("div");
  typing.className = "message assistant";
  typing.textContent = "Thinking...";
  messages.appendChild(typing);

  try {
    const res = await fetch(
      `${API}/chat/${studentId}?message=${encodeURIComponent(text)}`,
      { method: "POST" }
    );
    const data = await res.json();
    typing.remove();
    addMessage(data.reply || data.error || "No response", "assistant");
  } catch (e) {
    typing.remove();
    addMessage("Server error", "assistant");
  }
};

input.addEventListener("keydown", e => {
  if (e.key === "Enter") sendBtn.click();
});

newChat.onclick = () => {
  messages.innerHTML = "";
  addMessage("Hello! How can I help you?", "assistant");
};

logout.onclick = () => {
  localStorage.clear();
  window.location.href = "login.html";
};
