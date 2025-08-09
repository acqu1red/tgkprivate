(() => {
  const TG = window.Telegram?.WebApp;
  if (TG) TG.expand();

  const SUPABASE_URL = 'https://uhhsrtmmuwoxsdquimaa.supabase.co';
  const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVoaHNydG1tdXdveHNkcXVpbWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ2OTMwMzcsImV4cCI6MjA3MDI2OTAzN30.5xxo6g-GEYh4ufTibaAtbgrifPIU_ilzGzolAdmAnm8';
  const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

  const ADMIN_TELEGRAM_ID = '123456789'; // ЗАМЕНИТЕ на реальный

  const qs = new URLSearchParams(location.search);
  const forcedConversationId = qs.get('conversation_id');

  const chatEl = document.getElementById('chat');
  const textInput = document.getElementById('textInput');
  const sendBtn = document.getElementById('sendBtn');
  const fileInput = document.getElementById('fileInput');
  const adminPanelBtn = document.getElementById('adminPanelBtn');
  const adminPanel = document.getElementById('adminPanel');
  const closePanel = document.getElementById('closePanel');
  const conversationsEl = document.getElementById('conversations');
  const controls = document.getElementById('statusControls');
  const setPendingBtn = document.getElementById('setPending');
  const setDoneBtn = document.getElementById('setDone');

  const tgUser = TG?.initDataUnsafe?.user;
  const currentUserId = tgUser?.id?.toString() || 'unknown';
  const currentUsername = tgUser?.username || 'user';
  const isAdmin = (currentUserId === ADMIN_TELEGRAM_ID) || (qs.get('reply') === '1');

  if (!isAdmin) {
    adminPanelBtn.style.display = 'none';
    controls.classList.add('hidden');
  } else {
    controls.classList.remove('hidden');
  }

  function msgEl(role, text, dt) {
    const el = document.createElement('div');
    el.className = `msg ${role}`;
    el.innerHTML = `${(text || '').replace(/\n/g, '<br/>')}<div class=\"meta\">${new Date(dt).toLocaleString()}</div>`;
    return el;
  }
  function scrollBottom() { chatEl.scrollTo({ top: chatEl.scrollHeight, behavior: 'smooth' }); }

  let conversationId = forcedConversationId || null;

  async function ensureConversation() {
    if (conversationId) return conversationId;
    const { data, error } = await supabase
      .from('conversations')
      .insert({ user_id: currentUserId, username: currentUsername, status: 'open' })
      .select('id')
      .single();
    if (error) { console.error('ensureConversation error', error); throw error; }
    conversationId = data.id;
    return conversationId;
  }

  async function loadMessages() {
    if (!conversationId) return;
    const { data, error } = await supabase
      .from('messages')
      .select('*')
      .eq('conversation_id', conversationId)
      .order('created_at', { ascending: true });
    if (error) { console.error('loadMessages error', error); return; }
    chatEl.innerHTML = '';
    for (const m of data) {
      const role = m.sender_id === currentUserId ? 'user' : 'admin';
      chatEl.appendChild(msgEl(role, m.text || (m.file_url ? '📎 Вложение' : ''), m.created_at));
    }
    scrollBottom();
  }

  async function sendMessage(text, file) {
    try {
      const convId = await ensureConversation();
      let fileUrl = null;
      if (file) {
        const ext = (file.name.split('.').pop() || 'bin');
        const path = `${convId}/${Date.now()}_${Math.random().toString(36).slice(2)}.${ext}`;
        const { error: upErr } = await supabase.storage.from('attachments').upload(path, file, { upsert: false, contentType: file.type || 'application/octet-stream' });
        if (upErr) {
          console.error('upload error', upErr);
          alert('Не удалось загрузить файл');
        } else {
          const { data: pub } = supabase.storage.from('attachments').getPublicUrl(path);
          fileUrl = pub.publicUrl;
        }
      }
      const payload = { conversation_id: convId, sender_id: currentUserId, username: currentUsername, text: text || null, file_url: fileUrl, notified: false };
      const { error } = await supabase.from('messages').insert(payload);
      if (error) { console.error('insert message error', error); alert('Ошибка отправки: ' + (error.message || 'неизвестная')); return; }
      textInput.value = '';
      fileInput.value = '';
      await loadMessages();
    } catch (e) {
      console.error('sendMessage exception', e);
      alert('Ошибка: ' + (e.message || 'неизвестная'));
    }
  }

  function subscribeRealtime() {
    supabase.channel('messages-ch')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'messages' }, async (payload) => {
        if (payload.new?.conversation_id === conversationId) await loadMessages();
      })
      .subscribe();
  }

  sendBtn.addEventListener('click', async () => {
    const text = textInput.value.trim();
    const file = fileInput.files?.[0] || null;
    if (!text && !file) return;
    await sendMessage(text, file);
  });
  textInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); sendBtn.click(); } });

  adminPanelBtn.addEventListener('click', () => { if (!isAdmin) return; adminPanel.classList.remove('hidden'); setTimeout(() => adminPanel.classList.add('show'), 10); loadConversations(); });
  closePanel.addEventListener('click', () => { adminPanel.classList.remove('show'); setTimeout(() => adminPanel.classList.add('hidden'), 250); });

  async function loadConversations() {
    const { data, error } = await supabase.from('conversations').select('*').order('updated_at', { ascending: false }).limit(100);
    if (error) { console.error('loadConversations error', error); return; }
    conversationsEl.innerHTML = '';
    for (const c of data || []) {
      const item = document.createElement('div');
      item.className = 'item';
      item.innerHTML = `<div><b>@${c.username || 'user'}</b><div class=\"meta\">${new Date(c.updated_at).toLocaleString()} • ${c.status}</div></div><button data-id=\"${c.id}\">Открыть</button>`;
      item.querySelector('button').addEventListener('click', async () => { conversationId = c.id; await loadMessages(); });
      conversationsEl.appendChild(item);
    }
  }

  async function setStatus(status) { if (!conversationId) return; const { error } = await supabase.from('conversations').update({ status }).eq('id', conversationId); if (error) console.error('setStatus error', error); }
  setPendingBtn.addEventListener('click', () => isAdmin && setStatus('pending'));
  setDoneBtn.addEventListener('click', () => isAdmin && setStatus('done'));

  (async function init() { try { await ensureConversation(); await loadMessages(); subscribeRealtime(); } catch (e) { console.error('init error', e); } })();
})();
