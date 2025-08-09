from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

API_TOKEN = '8354723250:AAEWcX6OojEi_fN-RAekppNMVTAsQDU0wvo'
ADMIN_ID = 833263633  # ID администратора

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("💳 Оплатить доступ", callback_data='pay'))
    keyboard.add(InlineKeyboardButton("ℹ️ Подробнее о канале", callback_data='more_info'))
    keyboard.add(InlineKeyboardButton("❓ Задать вопрос", callback_data='ask_question'))
    await message.answer("<b>Приветствую.</b> Ты в официальном боте по оплате доступа к каналу ОСНОВА - где знания не просто ценные, а, жизненно необходимые.\n\n💳 Подписка - ежемесячная 1500₽ или ~15$, оплата принимается в любой валюте и крипте.\n⬇️ Ниже — кнопка. Жмешь — и проходишь туда, где люди не ноют, а ебут этот мир в обе щеки.\n\n💳 Подписка - ежемесячная 1500₽ или ~14$, оплату принимаем в любой валюте, крипте, звездах.\nНажимай кнопку ниже ⬇️", parse_mode=ParseMode.HTML, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'pay')
async def process_pay_callback(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("1 месяц", callback_data='pay_1_month'))
    keyboard.add(InlineKeyboardButton("6 месяцев", callback_data='pay_6_months'))
    keyboard.add(InlineKeyboardButton("12 месяцев", callback_data='pay_12_months'))
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='back_to_start'))
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text="💵 Стоимость подписки на Базу\n1 месяц 1500 рублей\n6 месяцев 8000 рублей\n12 месяцев 10 000 рублей\n\n*цена в долларах/евро - конвертируется по нынешнему курсу\n\n*оплачивай любой картой в долларах/евро/рублях, бот сконвертирует сам\n\nОплатить и получить доступ\n👇👇👇", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('pay_'))
async def process_subscription_callback(callback_query: types.CallbackQuery):
    subscription_period = callback_query.data.split('_')[1]
    period_text = {'1': '1 месяц', '6': '6 месяцев', '12': '12 месяцев'}[subscription_period]
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Карта (любая валюта)", callback_data='pay_card'))
    keyboard.add(InlineKeyboardButton("❓ Задать вопрос", callback_data='ask_question'))
    keyboard.add(InlineKeyboardButton("📜 Договор оферты", callback_data='offer_agreement'))
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='back_to_pay'))
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text=f"🦍 ЗАКРЫТЫЙ КАНАЛ \"ОСНОВА\" на {period_text}\nВыберите удобный вид оплаты:\n*если вы из Украины, включите vpn\n*при оплате картой - оформляется автосписание, каждые 30 дней\n*далее - вы сможете управлять подпиской в Меню бота\n*оплата криптой доступна на тарифах на 6/12 мес", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'more_info')
async def process_more_info_callback(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("❓ Задать вопрос", callback_data='ask_question'))
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='back_to_start'))
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text="ОСНОВА — это золотой рюкзак знаний, с которым ты можешь вылезти из любой жопы.\n\nТут не просто \"мотивация\" и \"развитие\", а рабочие схемы, которые ты не найдёшь даже если будешь копать ебучий Даркнет.\n\n🧠 Подкасты с таймкодами — от ПРОФАЙЛИНГА до манипуляций баб, от ПСИХОТИПОВ до коммуникации на уровне спецслужб\n💉 Органический БИОХАКИНГ — почему тебе плохо и как через неделю почувствовать себя богом\n💸 Уроки по ФРОДУ, где из нуля делается $5000+ в месяц, если не еблан\n🧱 Как выстроить дисциплину, отшить самобичевание и наконец стать машиной, а не мямлей\n📈 Авторские стратегии по трейдингу — от $500/мес на автопилоте\n⚡ Скальпинг и биржи — как хитрить систему, не теряя бабки на комиссиях\n🎥 Стримы каждые 2 недели, где разбираю вопросы подписчиков: здоровье, деньги, психика, мышление\n\nИ это лишь малая часть того, что тебя ожидает в Формуле.\n\nЭто не просто канал. Это сила, которая перестраивает твое мышление под нового тебя.\nВокруг тебя — миллион способов сделать бабки, использовать людей и не пахать, пока другие пашут.\n\nТы будешь считывать людей с его профиля в мессенджере, зарабатывать из воздуха и нести себя как король, потому что знаешь больше, чем они когда-либо поймут.\n\nКнопка внизу ⬇️. Там не просто инфа. Там выход из стада.\nРешай.", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'back_to_start')
async def process_back_to_start_callback(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("💳 Оплатить доступ", callback_data='pay'))
    keyboard.add(InlineKeyboardButton("ℹ️ Подробнее о канале", callback_data='more_info'))
    keyboard.add(InlineKeyboardButton("❓ Задать вопрос", callback_data='ask_question'))
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text="<b>Приветствую.</b> Ты в официальном боте по оплате доступа к каналу ОСНОВА - где знания не просто ценные, а, жизненно необходимые.\n\n💳 Подписка - ежемесячная 1500₽ или ~15$, оплата принимается в любой валюте и крипте.\n⬇️ Ниже — кнопка. Жмешь — и проходишь туда, где люди не ноют, а ебут этот мир в обе щеки.\n\n💳 Подписка - ежемесячная 1500₽ или ~14$, оплату принимаем в любой валюте, крипте, звездах.\nНажимай кнопку ниже ⬇️", parse_mode=ParseMode.HTML, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'back_to_pay')
async def process_back_to_pay_callback(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("1 месяц", callback_data='pay_1_month'))
    keyboard.add(InlineKeyboardButton("6 месяцев", callback_data='pay_6_months'))
    keyboard.add(InlineKeyboardButton("12 месяцев", callback_data='pay_12_months'))
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='back_to_start'))
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                text="💵 Стоимость подписки на Базу\n1 месяц 1500 рублей\n6 месяцев 8000 рублей\n12 месяцев 10 000 рублей\n\n*цена в долларах/евро - конвертируется по нынешнему курсу\n\n*оплачивай любой картой в долларах/евро/рублях, бот сконвертирует сам\n\nОплатить и получить доступ\n👇👇👇", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'ask_question')
async def process_ask_question_callback(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("❓ Задать вопрос", web_app=WebAppInfo(url="https://acqu1red.github.io/TGKaccount/")))
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data='back_to_start'))
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id, 
        message_id=callback_query.message.message_id,
        text="🎯 Есть вопросы? Нажмите кнопку ниже, чтобы открыть форму обратной связи.\n\nВы сможете задать свой вопрос администратору канала напрямую!", 
        reply_markup=keyboard
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
