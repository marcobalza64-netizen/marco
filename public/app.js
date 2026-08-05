const form = document.querySelector('#marco-form');
const input = document.querySelector('#message');
const replyEl = document.querySelector('#reply');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  replyEl.textContent = '…';
  replyEl.className = 'reply';

  try {
    const res = await fetch('/api/marco', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input.value }),
    });
    const data = await res.json();
    replyEl.textContent = data.reply;
    replyEl.classList.add(data.match ? 'match' : 'miss');
  } catch {
    replyEl.textContent = 'Something went wrong reaching the server.';
    replyEl.classList.add('miss');
  }
});
