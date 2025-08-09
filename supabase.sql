-- Таблицы
create table if not exists public.conversations (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  username text,
  status text not null default 'open', -- open | pending | done
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  sender_id text not null, -- telegram id, строкой
  username text,
  text text,
  file_url text,
  notified boolean not null default false,
  created_at timestamptz not null default now()
);

-- Триггер обновления updated_at
create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists conversations_set_updated_at on public.conversations;
create trigger conversations_set_updated_at
before update on public.conversations
for each row execute function public.set_updated_at();

-- Индексы
create index if not exists idx_messages_conv_created on public.messages(conversation_id, created_at);
create index if not exists idx_conversations_updated on public.conversations(updated_at);

-- Storage bucket для вложений (создайте bucket вручную с именем 'attachments' и public access)
-- В консоле Storage -> New bucket -> name: attachments -> Public bucket

-- RLS политики (при желании)
alter table public.conversations enable row level security;
alter table public.messages enable row level security;

-- Политики для анонимного доступа WebApp (анонимный ключ)
create policy if not exists "conversations_select" on public.conversations
for select using (true);
create policy if not exists "conversations_insert" on public.conversations
for insert with check (true);
create policy if not exists "conversations_update" on public.conversations
for update using (true);

create policy if not exists "messages_select" on public.messages
for select using (true);
create policy if not exists "messages_insert" on public.messages
for insert with check (true);
create policy if not exists "messages_update" on public.messages
for update using (true);
