document.addEventListener('DOMContentLoaded', () => {
    // Initialize Telegram WebApp (optional UI tweaks)
    if (window.Telegram && window.Telegram.WebApp) {
        try {
            Telegram.WebApp.expand();
            Telegram.WebApp.enableClosingConfirmation();
            Telegram.WebApp.ready();
        } catch (e) {
            console.warn('Telegram WebApp init warning:', e);
        }
    }
    const sendButton = document.getElementById('send-button');
    const messageInput = document.getElementById('message-input');
    const fileInput = document.getElementById('file-input');
    const chat = document.getElementById('chat');
    const adminButton = document.getElementById('admin-button');
    const adminList = document.getElementById('admin-list');

    // Подключение к Supabase
    const supabaseUrl = 'https://uhhsrtmmuwoxsdquimaa.supabase.co';
    const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVoaHNydG1tdXdveHNkcXVpbWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ2OTMwMzcsImV4cCI6MjA3MDI2OTAzN30.5xxo6g-GEYh4ufTibaAtbgrifPIU_ilzGzolAdmAnm8';
    const supabaseClient = window.supabase.createClient(supabaseUrl, supabaseKey);

    // Функция для добавления сообщения в Supabase
    async function addMessageToSupabase(userId, messageText) {
        const { data, error } = await supabaseClient
            .from('messages')
            .insert([{ user_id: userId, message_text: messageText }]);
        if (error) console.error('Ошибка при добавлении сообщения:', error);
        else console.log('Сообщение добавлено:', data);
    }

    // Функция для получения списка пользователей
    async function getUsersFromSupabase() {
        const { data, error } = await supabaseClient
            .from('users')
            .select('*');
        if (error) console.error('Ошибка при получении пользователей:', error);
        else return data;
    }

    // Обновление обработчика отправки сообщений
    sendButton.addEventListener('click', async () => {
        const messageText = messageInput.value;
        if (messageText.trim() !== '') {
            addMessageToChat(messageText, 'user');
            messageInput.value = '';
            // Добавление сообщения в Supabase
            await addMessageToSupabase(1, messageText); // Здесь 1 - это пример user_id
        }
    });

    // Обновление обработчика панели администратора
    adminButton.addEventListener('click', async () => {
        adminList.classList.toggle('hidden');
        if (!adminList.classList.contains('hidden')) {
            const users = await getUsersFromSupabase();
            adminList.innerHTML = users.map(user => `<div>${user.username}</div>`).join('');
        }
    });

    function addMessageToChat(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        messageElement.textContent = message;
        chat.appendChild(messageElement);
        chat.scrollTop = chat.scrollHeight;
    }
});
