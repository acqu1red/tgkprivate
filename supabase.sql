-- Таблица пользователей (для простоты Telegram user id и username)
create table if not exists users (
  id bigint primary key, -- Telegram user id
  username text,
  is_admin boolean default false,
  created_at timestamp with time zone default now()
);

-- Таблица диалогов (каждое новое сообщение пользователя — новый диалог)
create table if not exists dialogs (
  id uuid primary key default gen_random_uuid(),
  user_id bigint references users(id),
  status text check (status in ('open', 'pending', 'closed')) default 'open',
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

create index on dialogs(user_id);

-- Таблица сообщений (сообщения диалога)
create table if not exists messages (
  id uuid primary key default gen_random_uuid(),
  dialog_id uuid references dialogs(id) on delete cascade,
  sender text check (sender in ('user', 'admin')),
  content text,
  created_at timestamp with time zone default now()
);

create index on messages(dialog_id);

-- Триггер обновления updated_at в dialogs при изменении сообщений
create or replace function update_dialog_timestamp()
returns trigger as $$
begin
  update dialogs set updated_at = now() where id = NEW.dialog_id;
  return NEW;
end;
$$ language plpgsql;

create trigger trg_update_dialog_updated_at
after insert on messages
for each row execute procedure update_dialog_timestamp();
