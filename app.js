document.addEventListener('DOMContentLoaded', () => {
  // Telegram WebApp init
  if (window.Telegram && window.Telegram.WebApp) {
    try {
      Telegram.WebApp.expand();
      Telegram.WebApp.enableClosingConfirmation();
      Telegram.WebApp.ready();
    } catch (e) {
      console.warn('Telegram WebApp init warning:', e);
    }
  }

  const chat = document.getElementById('chat');
  const input = document.getElementById('inputMessage');
  const sendBtn = document.getElementById('sendBtn');
  const attachBtn = document.getElementById('attachBtn');

  // Supabase
  const supabaseUrl = 'https://uhhsrtmmuwoxsdquimaa.supabase.co';
  const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVoaHNydG1tdXdveHNkcXVpbWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ2OTMwMzcsImV4cCI6MjA3MDI2OTAzN30.5xxo6g-GEYh4ufTibaAtbgrifPIU_ilzGzolAdmAnm8';
  const supabaseClient = window.supabase.createClient(supabaseUrl, supabaseKey);

  function addMessage(text, fromUser = true) {
    if (!text.trim()) return;
    const msg = document.createElement('div');
    msg.className = 'message ' + (fromUser ? 'user' : 'admin');
    msg.textContent = text;
    chat.appendChild(msg);
    chat.scrollTo({ top: chat.scrollHeight, behavior: 'smooth' });
  }

  async function addMessageToSupabase(userId, messageText) {
    const { data, error } = await supabaseClient
      .from('messages')
      .insert([{ user_id: userId, message_text: messageText }]);
    if (error) console.error('Ошибка при добавлении сообщения:', error);
    else console.log('Сообщение добавлено:', data);
  }

  // Remove automatic replies
  // adminReply(text);

  // Add admin panel functionality
  const adminButton = document.getElementById('admin-button');
  const adminPanel = document.getElementById('admin-panel');

  adminButton.addEventListener('click', async () => {
    const { data: messages, error } = await supabaseClient
      .from('messages')
      .select('username, created_at, message_text')
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching messages:', error);
      return;
    }

    adminPanel.innerHTML = '';
    messages.forEach(message => {
      const messageDiv = document.createElement('div');
      messageDiv.textContent = `${message.username} - ${message.created_at} - ${message.message_text}`;
      adminPanel.appendChild(messageDiv);

      messageDiv.addEventListener('click', () => {
        // Open dialog with user
        // Add logic to handle dialog
      });
    });

    adminPanel.classList.toggle('hidden');
  });

  async function sendMessage() {
    const text = input.value.trim();
    if (text.length === 0) return;
    addMessage(text, true);
    input.value = '';
    try {
      await addMessageToSupabase(1, text); // TODO: заменить 1 на реальный user_id
    } catch (e) {
      console.warn('Ошибка при сохранении в Supabase:', e);
    }
  }

  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  attachBtn.addEventListener('click', () => {
    alert('Функция прикрепления файлов в демо отключена');
  });
});
