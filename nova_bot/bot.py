import os
import logging
import sys
from pathlib import Path
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

# ========== НАСТРОЙКА ЛОГИРОВАНИЯ ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ========== БЕЗОПАСНАЯ ЗАГРУЗКА ТОКЕНА ==========
def get_bot_token():
    """Получаем токен из переменных окружения TimeWeb"""
    token = os.getenv("BOT_TOKEN")
    if token:
        logger.info("✅ Токен получен из переменных окружения")
        return token
    
    logger.error("❌ BOT_TOKEN не найден!")
    logger.error("Добавьте переменную BOT_TOKEN в настройках TimeWeb")
    exit(1)

# Получаем токен
BOT_TOKEN = get_bot_token()
logger.info("✅ Токен успешно загружен.")

# ========== ИНИЦИАЛИЗАЦИЯ БОТА ==========
bot = Bot(
    token=BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ========== СОЗДАЁМ ГЛАВНОЕ МЕНЮ ==========
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🖼 Фото"), types.KeyboardButton(text="📸 Генерация"))
    builder.row(types.KeyboardButton(text="🎥 Видео"), types.KeyboardButton(text="🗣 Озвучка"))
    builder.row(types.KeyboardButton(text="🧠 Чат"), types.KeyboardButton(text="📊 Профиль"))
    builder.row(types.KeyboardButton(text="💎 Токены"))
    return builder.as_markup(resize_keyboard=True, input_field_placeholder="Выберите действие 👇")

# ========== КОМАНДА /start ==========
@dp.message(CommandStart())
async def start_command(message: Message):
    try:
        user_name = message.from_user.first_name or "друг"
        logger.info(f"🚀 /start от {message.from_user.id} ({user_name})")
        
        welcome_text = f"""🌟 <b>Привет, {user_name}!</b> Добро пожаловать в <b>NOVA AI</b>

✨ <b>Доступные функции:</b>
🖼  <b>Фото</b> — анимируй изображение
📸  <b>Генерация</b> — создай изображение
🎥  <b>Видео</b> — создание видео
🗣  <b>Озвучка</b> — текст в речь
🧠  <b>Чат</b> — общение с ИИ
📊  <b>Профиль</b> — баланс токенов
💎  <b>Токены</b> — пополнить баланс

🎁 <b>Новым пользователям +50 токенов!</b>
<b>Твой баланс: 150 токенов</b>

👇 <b>Выбери действие ниже</b>"""
        
        await message.answer(welcome_text, reply_markup=get_main_menu())
        
    except Exception as e:
        logger.error(f"❌ Ошибка в start_command: {e}")

# ========== КОМАНДА /menu ==========
@dp.message(Command("menu"))
async def menu_command(message: Message):
    try:
        logger.info(f"📱 Меню от {message.from_user.id}")
        await message.answer("📱 <b>Главное меню:</b>", reply_markup=get_main_menu())
    except Exception as e:
        logger.error(f"❌ Ошибка в menu_command: {e}")

# ========== КНОПКА "ТОКЕНЫ" ==========
@dp.message(F.text == "💎 Токены")
async def buy_command(message: Message):
    try:
        logger.info(f"💰 Токены от {message.from_user.id}")
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎫 40 токенов — 599₽", callback_data="buy_40")],
            [types.InlineKeyboardButton(text="🎫 80 токенов — 1099₽", callback_data="buy_80")],
            [types.InlineKeyboardButton(text="💎 400 токенов — 5099₽", callback_data="buy_400")],
            [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_menu")]
        ])
        
        text = """💎 <b>Покупка токенов</b>

<b>Выберите пакет:</b>
🎫 <b>40 токенов</b> — 599₽
🎫 <b>80 токенов</b> — 1099₽
💎 <b>400 токенов</b> — 5099₽

<b>Токены используются для:</b>
• Генерация изображений
• Оживление фото
• Создание видео
• Озвучка текста
• Нейро-чат

<b>Доставка мгновенно</b>"""
        
        await message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"❌ Ошибка в buy_command: {e}")

# ========== ОБРАБОТКА INLINE КНОПОК ==========
@dp.callback_query(F.data.startswith("buy_"))
async def handle_buy_callback(callback: CallbackQuery):
    try:
        await callback.answer("✅ Свяжитесь с администратором для оплаты", show_alert=True)
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_buy_callback: {e}")

@dp.callback_query(F.data == "back_menu")
async def handle_back_callback(callback: CallbackQuery):
    try:
        await callback.answer()
        await start_command(callback.message)
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_back_callback: {e}")

# ========== ОБРАБОТКА КНОПОК МЕНЮ ==========
@dp.message(F.text == "📊 Профиль")
async def profile_menu(message: Message):
    try:
        await message.answer(
            f"📊 <b>Профиль</b>\n\n"
            f"👤 <b>Имя:</b> {message.from_user.first_name}\n"
            f"🆔 <b>ID:</b> {message.from_user.id}\n"
            f"💎 <b>Токены:</b> 150\n\n"
            f"💎 Нажмите 'Токены' для пополнения"
        )
    except Exception as e:
        logger.error(f"❌ Ошибка в profile_menu: {e}")

@dp.message(F.text == "🖼 Фото")
async def animate_photo_info(message: Message):
    try:
        await message.answer("🖼 <b>Оживление фото</b>\n\nЗагрузите фото → получите анимацию!\n\n💎 <b>Стоимость:</b> 5 токенов")
    except Exception as e:
        logger.error(f"❌ Ошибка в animate_photo_info: {e}")

@dp.message(F.text == "📸 Генерация")
async def generate_photo_info(message: Message):
    try:
        await message.answer("📸 <b>Генерация фото</b>\n\nОпишите что хотите → AI создаст!\n\n💎 <b>Стоимость:</b> 3 токена")
    except Exception as e:
        logger.error(f"❌ Ошибка в generate_photo_info: {e}")

@dp.message(F.text == "🎥 Видео")
async def video_info(message: Message):
    try:
        await message.answer("🎥 <b>Видео</b>\n\nСоздам видео по сценарию!\n\n💎 <b>Стоимость:</b> 10 токенов")
    except Exception as e:
        logger.error(f"❌ Ошибка в video_info: {e}")

@dp.message(F.text == "🗣 Озвучка")
async def text_to_speech_info(message: Message):
    try:
        await message.answer("🗣 <b>Озвучка</b>\n\nТекст в речь!\n\n💎 <b>Стоимость:</b> 1 токен/100 символов")
    except Exception as e:
        logger.error(f"❌ Ошибка в text_to_speech_info: {e}")

@dp.message(F.text == "🧠 Чат")
async def neuro_chat_info(message: Message):
    try:
        await message.answer("🧠 <b>Чат</b>\n\nОбщайтесь с AI!\n\n💎 <b>Стоимость:</b> 1 токен/запрос\n\nНапишите вопрос...")
    except Exception as e:
        logger.error(f"❌ Ошибка в neuro_chat_info: {e}")

# ========== КОМАНДА /help ==========
@dp.message(Command("help"))
async def help_command(message: Message):
    try:
        await message.answer(
            "🆘 <b>Помощь</b>\n\n"
            "📌 <b>Команды:</b>\n"
            "/start - Запустить бота\n"
            "/menu - Показать меню\n"
            "/help - Помощь\n\n"
            "📱 <b>Используйте кнопки меню</b>"
        )
    except Exception as e:
        logger.error(f"❌ Ошибка в help_command: {e}")

# ========== КОМАНДА /buy ==========
@dp.message(Command("buy"))
async def buy_command_handler(message: Message):
    try:
        await buy_command(message)
    except Exception as e:
        logger.error(f"❌ Ошибка в buy_command_handler: {e}")

# ========== ОБРАБОТКА НЕИЗВЕСТНЫХ КОМАНД ==========
@dp.message()
async def unknown_command(message: Message):
    try:
        logger.info(f"❓ Неизвестная команда от {message.from_user.id}: {message.text}")
        await message.answer(
            "🤔 <b>Не понял команду</b>\n\n"
            "Используйте:\n"
            "/start - начало\n"
            "/menu - меню\n"
            "/help - помощь"
        )
    except Exception as e:
        logger.error(f"❌ Ошибка в unknown_command: {e}")

# ========== ЗАПУСК БОТА (ОПТИМИЗИРОВАНО ДЛЯ TIMEWEB) ==========
async def main():
    """Основная функция запуска"""
    try:
        logger.info("=" * 50)
        logger.info("🚀 Запуск бота NOVA AI на TimeWeb")
        logger.info("=" * 50)
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"🤖 Бот: @{bot_info.username} ({bot_info.full_name})")
        logger.info(f"🆔 ID бота: {bot_info.id}")
        
        # Удаляем вебхук и используем поллинг
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Вебхук удален, используем поллинг")
        
        # Запускаем поллинг
        logger.info("🔄 Запускаем поллинг...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        # TimeWeb автоматически перезапустит приложение
        raise
    finally:
        await bot.session.close()
        logger.info("🛑 Бот остановлен")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())