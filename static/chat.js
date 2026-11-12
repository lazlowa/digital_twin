// Chat panel: keeps the conversation in memory, streams replies from /api/chat.

const panel = document.getElementById("chat");
const log = document.getElementById("chat-log");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const send = document.getElementById("chat-send");
const starters = document.getElementById("chat-starters");

const history = [];
let busy = false;

const maxHistory = Number(form.dataset.maxHistory);
const ERRORS = {
  422: "That message could not be sent. Please shorten it and try again.",
  429: "You're sending messages quickly. Please wait a moment and try again.",
  default: "Sorry, something went wrong. Please try again in a moment.",
};

function updateSend() {
  send.disabled = busy || !input.value.trim();
}

function addMessage(role) {
  const element = document.createElement("div");
  element.className = `msg msg-${role}`;
  log.append(element);
  return element;
}

function scrollDown() {
  log.scrollTop = log.scrollHeight;
}

async function ask(question) {
  busy = true;
  updateSend();
  starters?.remove();
  history.push({ role: "user", content: question });
  addMessage("visitor").textContent = question;
  const reply = addMessage("twin");
  reply.classList.add("pending");
  reply.innerHTML = '<span class="typing" aria-label="Typing"><i></i><i></i><i></i></span>';
  scrollDown();

  let text = "";
  let errorText = ERRORS.default;
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // The server limits the history length; older turns are dropped first.
      // The history ends with the new question, so an odd count keeps the
      // window starting with a visitor message.
      body: JSON.stringify({ messages: history.slice(-(maxHistory - 1 + (maxHistory % 2))) }),
    });
    if (!response.ok) {
      errorText = ERRORS[response.status] || ERRORS.default;
      throw new Error(`HTTP ${response.status}`);
    }
    const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      text += value;
      reply.classList.remove("pending");
      reply.innerHTML = renderMarkdown(text);
      scrollDown();
    }
    if (!text.trim()) throw new Error("Empty reply");
    history.push({ role: "assistant", content: text });
  } catch (error) {
    console.error("Chat request failed:", error);
    history.pop();
    reply.classList.remove("pending");
    reply.classList.add("msg-error");
    reply.textContent = errorText;
    if (!input.value) input.value = question;
  } finally {
    busy = false;
    updateSend();
    scrollDown();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = input.value.trim();
  if (busy || !question) return;
  input.value = "";
  ask(question);
});

input.addEventListener("input", updateSend);
input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    form.requestSubmit();
  }
});

starters?.addEventListener("click", (event) => {
  const button = event.target.closest("button");
  if (button && !busy) ask(button.textContent.trim());
});

panel.addEventListener("toggle", (event) => {
  if (event.newState === "open") input.focus();
});

// Minimal Markdown: paragraphs, lists, headings (as bold), bold, italic, inline
// code and http(s)/mailto links. Everything else is escaped.

function escapeHtml(text) {
  const entities = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
  return text.replace(/[&<>"']/g, (char) => entities[char]);
}

function renderInline(text) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*\w])\*(?!\s)([^*]+?)\*/g, "$1<em>$2</em>")
    .replace(
      /\[([^\]]+)\]\(((?:https?:\/\/|mailto:)[^\s)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener">$1</a>',
    );
}

function renderMarkdown(text) {
  const html = [];
  let paragraph = [];
  let list = null;
  const flushParagraph = () => {
    if (paragraph.length) html.push(`<p>${renderInline(paragraph.join(" "))}</p>`);
    paragraph = [];
  };
  const closeList = () => {
    if (list) html.push(`</${list}>`);
    list = null;
  };

  for (const line of text.split("\n")) {
    const item = line.match(/^\s*(?:[-*+]|(\d+)[.)])\s+(.*)$/);
    const heading = line.match(/^#{1,6}\s+(.*)$/);
    if (item) {
      flushParagraph();
      const type = item[1] ? "ol" : "ul";
      if (list !== type) {
        closeList();
        html.push(`<${type}>`);
        list = type;
      }
      html.push(`<li>${renderInline(item[2])}</li>`);
    } else if (heading) {
      flushParagraph();
      closeList();
      html.push(`<p><strong>${renderInline(heading[1])}</strong></p>`);
    } else if (!line.trim()) {
      flushParagraph();
      closeList();
    } else {
      closeList();
      paragraph.push(line.trim());
    }
  }
  flushParagraph();
  closeList();
  return html.join("");
}
