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

  const adminId = 708907063;
  const adminPanelButton = document.createElement('button');
  adminPanelButton.id = 'admin-button';
  adminPanelButton.textContent = 'Панель Администратора';
  document.getElementById('input-area').appendChild(adminPanelButton);

  adminPanelButton.addEventListener('click', async () => {
    const { data: messages, error } = await supabaseClient
      .from('messages')
      .select('username, created_at, message_text')
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Ошибка при получении сообщений:', error);
      return;
    }

    const userMessages = messages.reduce((acc, message) => {
      if (!acc[message.username]) {
        acc[message.username] = [];
      }
      acc[message.username].push(message);
      return acc;
    }, {});

    const userList = Object.entries(userMessages).map(([username, msgs]) => {
      return {
        username,
        lastMessageDate: msgs[0].created_at,
        messageCount: msgs.length,
      };
    });

    console.log('Список пользователей:', userList);
  });

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

  // Удаляем автоматические ответы
  // function adminReply(userText) {
  //   const replies = [
  //     'Спасибо за сообщение, я сейчас посмотрю.',
  //     'Понял, держите меня в курсе.',
  //     'Могу помочь с этим вопросом, расскажите подробнее.',
  //     'Ваш запрос принят, скоро свяжемся.',
  //     'Спасибо за обратную связь!',
  //   ];
  //   const reply = replies[Math.floor(Math.random() * replies.length)];
  //   setTimeout(() => { addMessage(reply, false); }, 1200);
  // }

  function openUserDialog(username) {
    const dialog = document.createElement('div');
    dialog.className = 'dialog';

    const dialogHeader = document.createElement('h3');
    dialogHeader.textContent = `Диалог с ${username}`;
    dialog.appendChild(dialogHeader);

    const dialogMessages = document.createElement('div');
    dialogMessages.className = 'dialog-messages';
    dialog.appendChild(dialogMessages);

    const underReviewButton = document.createElement('button');
    underReviewButton.textContent = 'На рассмотрении';
    underReviewButton.addEventListener('click', () => {
      console.log(`Диалог с ${username} на рассмотрении`);
    });
    dialog.appendChild(underReviewButton);

    const completedButton = document.createElement('button');
    completedButton.textContent = 'Закончен';
    completedButton.addEventListener('click', () => {
      console.log(`Диалог с ${username} завершен`);
    });
    dialog.appendChild(completedButton);

    document.body.appendChild(dialog);
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (text.length === 0) return;
    addMessage(text, true);
    input.value = '';
    const userId = window.Telegram.WebApp.initDataUnsafe.user.id; // Получаем реальный user_id
    try {
      await addMessageToSupabase(userId, text);
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
