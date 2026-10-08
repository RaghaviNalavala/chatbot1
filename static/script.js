const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const chatWindow = document.getElementById('chatWindow');
const quickQuestions = document.querySelectorAll('.quick-question');

function addMessage(role, text) {
  const wrapper = document.createElement('div');
  wrapper.className = `message ${role}`;

  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';
  bubble.textContent = text;

  wrapper.appendChild(bubble);
  chatWindow.appendChild(wrapper);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function setLoading(isLoading) {
  const submitButton = chatForm.querySelector('button');
  submitButton.disabled = isLoading;
  submitButton.textContent = isLoading ? 'Thinking...' : 'Send';
}

async function sendMessage(message) {
  addMessage('user', message);
  setLoading(true);

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    const reply = data.reply || 'Sorry, I could not generate a response right now.';
    addMessage('bot', reply);
  } catch (error) {
    addMessage('bot', 'There was a problem connecting to the chatbot. Please try again in a moment.');
  } finally {
    setLoading(false);
    chatInput.value = '';
    chatInput.focus();
  }
}

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = chatInput.value.trim();

  if (!message) {
    chatInput.focus();
    return;
  }

  await sendMessage(message);
});

quickQuestions.forEach((button) => {
  button.addEventListener('click', () => {
    chatInput.value = button.textContent;
    chatInput.focus();
  });
});
