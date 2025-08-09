from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from supabase import create_client, Client
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler
import asyncio
import uvicorn

# Конфиги
SUPABASE_URL = "https://uhhsrtmmuwoxsdquimaa.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVoaHNydG1tdXdveHNkcXVpbWFhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ2OTMwMzcsImV4cCI6MjA3MDI2OTAzN30.5xxo6g-GEYh4ufTibaAtbgrifPIU_ilzGzolAdmAnm8"
ADMIN_TELEGRAM_ID = 708907063
BOT_TOKEN = "ВАШ_ТОКЕН_БОТА"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bot = Bot(token=BOT_TOKEN)

app = FastAPI()

# Модели
class User(BaseModel):
    id: int
    username: Optional[str]

class MessageCreate(BaseModel):
    dialog_id: str
    sender: str
    content: str

class DialogCreate(BaseModel):
    user_id: int

class NotifyPayload(BaseModel):
    user_id: int
    username: Optional[str]
    dialog_id: str
    message: str

# --- API ---

@app.post("/users/")
async def create_or_get_user(user: User):
    # Проверяем есть ли пользователь
    data = supabase.table("users").select("*").eq("id", user.id).execute()
    if data.data and len(data.data) > 0:
        return data.data[0]
    # Создаем
    res = supabase.table("users").insert({
        "id": user.id,
        "username": user.username,
        "is_admin": False
    }).execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)
    return res.data[0]

@app.post("/dialogs/")
async def create_dialog(dialog: DialogCreate):
    res = supabase.table("dialogs").insert({
        "user_id": dialog.user_id,
        "status": "open"
    }).execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)
    return res.data[0]

@app.get("/dialogs/{user_id}")
async def get_dialogs(user_id: int):
    res = supabase.table("dialogs").select("*").eq("user_id", user_id).order("updated_at", desc=True).execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)
    return res.data

@app.get("/dialogs/admin")
async def get_open_dialogs():
    res = supabase.table("dialogs").select("*, user:users(id, username)").neq("status", "closed").order("updated_at", desc=True).execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)
    return res.data

@app.get("/messages/{dialog_id}")
async def get_messages(dialog_id: str):
    res = supabase.table("messages").select("*").eq("dialog_id", dialog_id).order("created_at", asc=True).execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)
    return res.data

@app.post("/messages/")
async def post_message(msg: MessageCreate):
    res = supabase.table("messages").insert({
        "dialog_id": msg.dialog_id,
        "sender": msg.sender,
        "content": msg.content
    }).execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)

    # Обновляем updated_at диалога (Supabase триггер сделает это, но можно подстраховаться)
    supabase.table("dialogs").update({"updated_at": "now()"}).eq("id", msg.dialog_id).execute()

    # Если сообщение от пользователя, отправляем уведомление админу
    if msg.sender == "user":
        # Получаем диалог и пользователя для уведомления
        dialogs = supabase.table("dialogs").select("*").eq("id", msg.dialog_id).execute()
        if dialogs.data and len(dialogs.data) > 0:
            dialog = dialogs.data[0]
            users = supabase.table("users").select("*").eq("id", dialog['user_id']).execute()
            username = users.data[0]['username'] if users.data and len(users.data) > 0 else 'unknown'
            await notify_admin(dialog['user_id'], username, msg.dialog_id, msg.content)
    return res.data[0]

@app.post("/dialogs/{dialog_id}/status")
async def update_dialog_status(dialog_id: str, status: str):
    if status not in ('open', 'pending', 'closed'):
        raise HTTPException(status_code=400, detail="Invalid status")
    res = supabase.table("dialogs").update({"status": status}).eq("id", dialog_id).execute()
    if res.error:
        raise HTTPException(status_code=400, detail=res.error.message)
    return {"message": "Status updated"}

# --- Telegram уведомления ---

async def notify_admin(user_id, username, dialog_id, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ответить", callback_data=f"reply_{user_id}_{dialog_id}")]
    ])
    text = f"Новый вопрос от @{username} (ID: {user_id}):\n\n{message}\n\nНажмите кнопку, чтобы ответить."
    await bot.send_message(chat_id=ADMIN_TELEGRAM_ID, text=text, reply_markup=keyboard)

# Здесь можно добавить обработчик CallbackQueryHandler, но для FastAPI это нужно отдельно

# --- Запуск сервера ---

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
