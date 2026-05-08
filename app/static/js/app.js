// Chatbot flotante
(function () {
  const toggle = document.getElementById('chatbot-toggle');
  const win = document.getElementById('chatbot-window');
  const close = document.getElementById('chatbot-close');
  const form = document.getElementById('chatbot-form');
  const input = document.getElementById('chatbot-input');
  const messages = document.getElementById('chatbot-messages');
  if (!toggle) return;

  toggle.addEventListener('click', () => win.classList.toggle('d-none'));
  close.addEventListener('click', () => win.classList.add('d-none'));

  function addMessage(text, who) {
    const div = document.createElement('div');
    div.className = 'msg ' + who;
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const msg = input.value.trim();
    if (!msg) return;
    addMessage(msg, 'user');
    input.value = '';
    addMessage('...', 'bot');
    try {
      const r = await fetch('/api/chatbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      const data = await r.json();
      messages.lastChild.remove(); // quitar "..."
      addMessage(data.reply, 'bot');
    } catch (err) {
      messages.lastChild.remove();
      addMessage('Error de conexión.', 'bot');
    }
  });
})();
