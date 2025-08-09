import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder


logging.basicConfig(level=logging.INFO)


def build_start_keyboard() -> InlineKeyboardBuilder:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.row(InlineKeyboardButton(text="💳 Оплатить доступ", callback_data="pay"))
    keyboard_builder.row(InlineKeyboardButton(text="ℹ️ Подробнее о канале", callback_data="more_info"))
    keyboard_builder.row(InlineKeyboardButton(text="❓ Задать вопрос", callback_data="ask_question"))
    return keyboard_builder


def build_pay_keyboard() -> InlineKeyboardBuilder:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.row(InlineKeyboardButton(text="1 месяц", callback_data="pay_1_month"))
    keyboard_builder.row(InlineKeyboardButton(text="6 месяцев", callback_data="pay_6_months"))
    keyboard_builder.row(InlineKeyboardButton(text="12 месяцев", callback_data="pay_12_months"))
    keyboard_builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_start"))
    return keyboard_builder


def build_subscription_keyboard() -> InlineKeyboardBuilder:
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.row(InlineKeyboardButton(text="Карта (любая валюта)", callback_data="pay_card"))
    keyboard_builder.row(InlineKeyboardButton(text="❓ Задать вопрос", callback_data="ask_question"))
    keyboard_builder.row(InlineKeyboardButton(text="📜 Договор оферты", callback_data="offer_agreement"))
    keyboard_builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_pay"))
    return keyboard_builder


router = Router()


@router.message(CommandStart())
async def send_welcome(message: Message) -> None:
    start_text = (
        "<b>Приветствую.</b> Ты в официальном боте по оплате доступа к каналу ОСНОВА - где знания не просто ценные, а, жизненно необходимые.\n\n"
        "💳 Подписка - ежемесячная 1500₽ или ~15$, оплата принимается в любой валюте и крипте.\n"
        "⬇️ Ниже — кнопка. Жмешь — и проходишь туда, где люди не ноют, а ебут этот мир в обе щеки.\n\n"
        "💳 Подписка - ежемесячная 1500₽ или ~14$, оплату принимаем в любой валюте, крипте, звездах.\n"
        "Нажимай кнопку ниже ⬇️"
    )
    await message.answer(start_text, reply_markup=build_start_keyboard().as_markup())


@router.callback_query(F.data == "pay")
async def process_pay_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text(
        (
            "💵 Стоимость подписки на Базу\n"
            "1 месяц 1500 рублей\n6 месяцев 8000 рублей\n12 месяцев 10 000 рублей\n\n"
            "*цена в долларах/евро - конвертируется по нынешнему курсу\n\n"
            "*оплачивай любой картой в долларах/евро/рублях, бот сконвертирует сам\n\n"
            "Оплатить и получить доступ\n👇👇👇"
        ),
        reply_markup=build_pay_keyboard().as_markup(),
    )


@router.callback_query(F.data.startswith("pay_"))
async def process_subscription_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    parts = callback.data.split("_") if callback.data else []
    period_key = parts[1] if len(parts) > 1 else "1"
    period_text = {"1": "1 месяц", "6": "6 месяцев", "12": "12 месяцев"}.get(period_key, "1 месяц")
    await callback.message.edit_text(
        (
            f"🦍 ЗАКРЫТЫЙ КАНАЛ \"ОСНОВА\" на {period_text}\n"
            "Выберите удобный вид оплаты:\n"
            "*если вы из Украины, включите vpn\n"
            "*при оплате картой - оформляется автосписание, каждые 30 дней\n"
            "*далее - вы сможете управлять подпиской в Меню бота\n"
            "*оплата криптой доступна на тарифах на 6/12 мес"
        ),
        reply_markup=build_subscription_keyboard().as_markup(),
    )


@router.callback_query(F.data == "more_info")
async def process_more_info_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    info_text = (
        "ОСНОВА — это золотой рюкзак знаний, с которым ты можешь вылезти из любой жопы.\n\n"
        "Тут не просто \"мотивация\" и \"развитие\", а рабочие схемы, которые ты не найдёшь даже если будешь копать ебучий Даркнет.\n\n"
        "🧠 Подкасты с таймкодами — от ПРОФАЙЛИНГА до манипуляций баб, от ПСИХОТИПОВ до коммуникации на уровне спецслужб\n"
        "💉 Органический БИОХАКИНГ — почему тебе плохо и как через неделю почувствовать себя богом\n"
        "💸 Уроки по ФРОДУ, где из нуля делается $5000+ в месяц, если не еблан\n"
        "🧱 Как выстроить дисциплину, отшить самобичевание и наконец стать машиной, а не мямлей\n"
        "📈 Авторские стратегии по трейдингу — от $500/мес на автопилоте\n"
        "⚡ Скальпинг и биржи — как хитрить систему, не теряя бабки на комиссиях\n"
        "🎥 Стримы каждые 2 недели, где разбираю вопросы подписчиков: здоровье, деньги, психика, мышление\n\n"
        "И это лишь малая часть того, что тебя ожидает в Формуле.\n\n"
        "Это не просто канал. Это сила, которая перестраивает твое мышление под нового тебя.\n"
        "Вокруг тебя — миллион способов сделать бабки, использовать людей и не пахать, пока другие пашут.\n\n"
        "Ты будешь считывать людей с его профиля в мессенджере, зарабатывать из воздуха и нести себя как король, потому что знаешь больше, чем они когда-либо поймут.\n\n"
        "Кнопка внизу ⬇️. Там не просто инфа. Там выход из стада.\n"
        "Решай."
    )
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.row(InlineKeyboardButton(text="❓ Задать вопрос", callback_data="ask_question"))
    keyboard_builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_start"))
    await callback.message.edit_text(info_text, reply_markup=keyboard_builder.as_markup())


@router.callback_query(F.data == "ask_question")
async def process_ask_question_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.row(
        InlineKeyboardButton(
            text="Открыть мини-приложение",
            url="https://acqu1red.github.io/tgkprivate/",
        )
    )
    await callback.message.answer(
        "Откройте мини-приложение для отправки вопроса:",
        reply_markup=keyboard_builder.as_markup(),
    )


@router.callback_query(F.data == "back_to_start")
async def process_back_to_start_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    start_text = (
        "<b>Приветствую.</b> Ты в официальном боте по оплате доступа к каналу ОСНОВА - где знания не просто ценные, а, жизненно необходимые.\n\n"
        "💳 Подписка - ежемесячная 1500₽ или ~15$, оплата принимается в любой валюте и крипте.\n"
        "⬇️ Ниже — кнопка. Жмешь — и проходишь туда, где люди не ноют, а ебут этот мир в обе щеки.\n\n"
        "💳 Подписка - ежемесячная 1500₽ или ~14$, оплату принимаем в любой валюте, крипте, звездах.\n"
        "Нажимай кнопку ниже ⬇️"
    )
    await callback.message.edit_text(start_text, reply_markup=build_start_keyboard().as_markup())


@router.callback_query(F.data == "back_to_pay")
async def process_back_to_pay_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text(
        (
            "💵 Стоимость подписки на Базу\n"
            "1 месяц 1500 рублей\n6 месяцев 8000 рублей\n12 месяцев 10 000 рублей\n\n"
            "*цена в долларах/евро - конвертируется по нынешнему курсу\n\n"
            "*оплачивай любой картой в долларах/евро/рублях, бот сконвертирует сам\n\n"
            "Оплатить и получить доступ\n👇👇👇"
        ),
        reply_markup=build_pay_keyboard().as_markup(),
    )


async def main() -> None:
    # Load environment variables from .env if present
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except Exception:
        pass

    token = os.getenv("BOT_TOKEN")
    if not token:
        logging.warning("BOT_TOKEN is not set; falling back to embedded token")
        token = "8354723250:AAEWcX6OojEi_fN-RAekppNMVTAsQDU0wvo"

    bot = Bot(token=token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())


