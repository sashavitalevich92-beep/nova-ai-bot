import os
import logging
import sys
import uuid
import re
import aiohttp
from datetime import datetime, date
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

# ========== 🔐 ТВОИ ДАННЫЕ (ВСТАВЬ СЮДА) ==========
BOT_TOKEN = "8253186876:AAHAFw7Q_Fsb0ijB_ZTYadXDq6W5aouCxsc" 
ADMIN_ID = 5024281589
API_URL = "http://127.0.0.1:8000" 
# =================================================

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

# ========== ИНИЦИАЛИЗАЦИЯ БОТА ==========
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ========== ТАРИФЫ ==========
TARIFFS = {
    "40": {"name": "40 токенов", "price": 240, "old_price": 599, "description": "🎫 Стартовый"},
    "80": {"name": "80 токенов", "price": 440, "old_price": 1099, "description": "🎫 Оптимальный"},
    "400": {"name": "400 токенов", "price": 2040, "old_price": 5099, "description": "💎 Выгодный"},
    "800": {"name": "800 токенов", "price": 3800, "old_price": 7600, "description": "👑 Максимальный ⭐"}
}

# ========== 📊 ХРАНИЛИЩЕ ДАННЫХ ==========
user_balances = {}          # Балансы токенов
user_welcome_received = {}  # Получили приветственные токены
user_stats = {
    "total_users": 0,       # Всего пользователей
    "active_today": 0,      # Активных сегодня
    "registered_users": set(),  # Уникальные пользователи
    "last_active": {},      # Последняя активность
    "total_payments": 0,    # Всего платежей
    "total_revenue": 0      # Всего выручка
}

# ========== 📊 ФУНКЦИИ СТАТИСТИКИ ==========
def update_user_stats(user_id: int):
    """Обновляет статистику пользователя"""
    user_stats["registered_users"].add(user_id)
    user_stats["total_users"] = len(user_stats["registered_users"])
    
    today = date.today().isoformat()
    user_stats["last_active"][user_id] = today
    
    active_today = 0
    for uid, last_date in user_stats["last_active"].items():
        if last_date == today:
            active_today += 1
    user_stats["active_today"] = active_today

def get_stats_text() -> str:
    """Возвращает красиво отформатированную статистику"""
    today = date.today().strftime('%d.%m.%Y')
    
    stats_text = f"""📊 <b>СТАТИСТИКА БОТА</b>
━━━━━━━━━━━━━━━━━━━━━
👥 <b>Пользователи:</b>
├ Всего: <b>{user_stats['total_users']}</b>
└ Активных сегодня: <b>{user_stats['active_today']}</b>

💰 <b>Финансы:</b>
├ Всего платежей: <b>{user_stats.get('total_payments', 0)}</b>
└ Выручка: <b>{user_stats.get('total_revenue', 0)}₽</b>

📅 <b>Дата:</b> {today}
━━━━━━━━━━━━━━━━━━━━━
🔄 Обновляется автоматически"""
    
    return stats_text

def get_user_balance(user_id: int) -> int:
    if user_id not in user_balances:
        user_balances[user_id] = 150
    return user_balances[user_id]

def add_user_balance(user_id: int, amount: int):
    if user_id not in user_balances:
        user_balances[user_id] = 150
    user_balances[user_id] += amount
    logger.info(f"💰 Пользователь {user_id} получил {amount} токенов. Баланс: {user_balances[user_id]}")

# ========== ГЛАВНОЕ МЕНЮ ==========
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="🖼 Фото"),
        types.KeyboardButton(text="📸 Генерация"),
        types.KeyboardButton(text="🎥 Видео"),
        types.KeyboardButton(text="🗣 Озвучка")
    )
    builder.row(
        types.KeyboardButton(text="🧠 Чат"),
        types.KeyboardButton(text="📊 Профиль"),
        types.KeyboardButton(text="💎 Токены")
    )
    return builder.as_markup(resize_keyboard=True)

# ========== 👑 МЕНЮ ДЛЯ АДМИНА ==========
def get_admin_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="🖼 Фото"),
        types.KeyboardButton(text="📸 Генерация"),
        types.KeyboardButton(text="🎥 Видео"),
        types.KeyboardButton(text="🗣 Озвучка")
    )
    builder.row(
        types.KeyboardButton(text="🧠 Чат"),
        types.KeyboardButton(text="📊 Профиль"),
        types.KeyboardButton(text="💎 Токены")
    )
    builder.row(
        types.KeyboardButton(text="📊 Статистика"),
        types.KeyboardButton(text="📢 Рассылка")
    )
    return builder.as_markup(resize_keyboard=True)

# ========== СТАРТ ==========
@dp.message(CommandStart())
async def start_command(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "друг"
    
    # 📊 Обновляем статистику
    update_user_stats(user_id)
    get_user_balance(user_id)
    
    logger.info(f"🚀 /start от {user_id} ({user_name})")
    
    # 👑 Выбираем меню в зависимости от прав
    menu = get_admin_menu() if user_id == ADMIN_ID else get_main_menu()
    
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
<b>Твой баланс: {get_user_balance(user_id)} токенов</b>

👇 <b>Выбери действие ниже</b>"""
    
    await message.answer(welcome_text, reply_markup=menu)

# ========== МЕНЮ ==========
@dp.message(Command("menu"))
async def menu_command(message: Message):
    menu = get_admin_menu() if message.from_user.id == ADMIN_ID else get_main_menu()
    await message.answer("📋 <b>Главное меню</b>", reply_markup=menu)

# ========== ПРОФИЛЬ ==========
@dp.message(Command("profile"))
@dp.message(F.text == "📊 Профиль")
async def profile_menu(message: Message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    
    await message.answer(
        f"📊 <b>Профиль</b>\n\n"
        f"👤 <b>Имя:</b> {message.from_user.first_name}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"💎 <b>Токены:</b> {balance}\n\n"
        f"🎁 Получи +50 токенов в разделе «Токены»",
        reply_markup=get_main_menu()
    )

# ========== БАЛАНС ==========
@dp.message(Command("balance"))
async def balance_command(message: Message):
    balance = get_user_balance(message.from_user.id)
    await message.answer(f"💰 <b>Ваш баланс:</b> {balance} токенов")

# ========== ТОКЕНЫ ==========
@dp.message(Command("buy"))
@dp.message(F.text == "💎 Токены")
async def buy_command(message: Message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    
    builder = InlineKeyboardBuilder()
    
    for key, tariff in TARIFFS.items():
        builder.row(InlineKeyboardButton(
            text=f"{tariff['description']} — {tariff['price']}₽ (-60%)",
            callback_data=f"pay_{key}"
        ))
    
    if not user_welcome_received.get(user_id, False):
        builder.row(InlineKeyboardButton(
            text="🎁 Получить 50 токенов — 0₽",
            callback_data="welcome_tokens"
        ))
    
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_menu"))
    
    text = f"""💎 <b>Покупка токенов</b>

<b>Выберите пакет:</b>
🎫 <b>40 токенов</b> — 240₽ (было 599₽)
🎫 <b>80 токенов</b> — 440₽ (было 1099₽)
💎 <b>400 токенов</b> — 2040₽ (было 5099₽)
👑 <b>800 токенов</b> — 3800₽ (было 7600₽)

💰 <b>Твой баланс:</b> {balance} токенов"""
    
    await message.answer(text, reply_markup=builder.as_markup())

# ========== ПРИВЕТСТВЕННЫЕ ТОКЕНЫ ==========
@dp.callback_query(F.data == "welcome_tokens")
async def welcome_tokens(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_welcome_received.get(user_id, False):
        await callback.answer("🎁 Вы уже получали приветственные токены!", show_alert=True)
        return
    
    add_user_balance(user_id, 50)
    user_welcome_received[user_id] = True
    
    await callback.answer("🎁 +50 токенов!", show_alert=True)
    await callback.message.edit_text(
        f"✅ <b>+50 токенов зачислено!</b>\n\n"
        f"💰 Баланс: {get_user_balance(user_id)} токенов",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="🎯 Купить ещё", callback_data="back_to_tariffs")
            ]]
        )
    )

# ========== ПЛАТЕЖИ ==========
@dp.callback_query(F.data.startswith("pay_"))
async def handle_payment(callback: CallbackQuery):
    await callback.answer("🔄 Создаём платёж...")
    tariff_key = callback.data.replace('pay_', '')
    tariff = TARIFFS[tariff_key]
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/create_payment/{tariff['price']}") as resp:
                data = await resp.json()
                
                if "confirmation_url" in data:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text=f"💳 Оплатить {tariff['price']}₽",
                            url=data['confirmation_url']
                        )],
                        [InlineKeyboardButton(
                            text="✅ Проверить",
                            callback_data=f"check_{data['payment_id']}_{tariff_key}"
                        )],
                        [InlineKeyboardButton(
                            text="◀️ Назад",
                            callback_data="back_to_tariffs"
                        )]
                    ])
                    
                    await callback.message.edit_text(
                        f"🧾 <b>Заказ #{data['payment_id'][:8]}</b>\n\n"
                        f"Тариф: {tariff['name']}\n"
                        f"Сумма: {tariff['price']}₽",
                        reply_markup=keyboard
                    )
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка: {str(e)[:100]}")

@dp.callback_query(F.data.startswith("check_"))
async def check_payment(callback: CallbackQuery):
    await callback.answer("🔄 Проверяем...")
    parts = callback.data.split('_')
    payment_id = parts[1]
    tariff_key = parts[2]
    tariff = TARIFFS[tariff_key]
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/payment/{payment_id}") as resp:
                data = await resp.json()
                
                if data.get('status') == 'succeeded':
                    user_id = callback.from_user.id
                    tokens_amount = int(tariff_key)
                    add_user_balance(user_id, tokens_amount)
                    
                    # 📊 Обновляем финансовую статистику
                    user_stats['total_payments'] = user_stats.get('total_payments', 0) + 1
                    user_stats['total_revenue'] = user_stats.get('total_revenue', 0) + tariff['price']
                    
                    await callback.message.edit_text(
                        f"✅ <b>Оплата успешна!</b>\n\n"
                        f"+{tokens_amount} токенов\n"
                        f"💰 Баланс: {get_user_balance(user_id)}",
                        reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=[[
                                InlineKeyboardButton(text="🎯 Купить ещё", callback_data="back_to_tariffs")
                            ]]
                        )
                    )
                else:
                    await callback.answer("⏳ Не завершён", show_alert=True)
    except:
        await callback.answer("❌ Ошибка", show_alert=True)

# ========== НАЗАД ==========
@dp.callback_query(F.data == "back_to_tariffs")
async def back_to_tariffs(callback: CallbackQuery):
    await callback.answer()
    await buy_command(callback.message)

@dp.callback_query(F.data == "back_menu")
async def back_menu(callback: CallbackQuery):
    await callback.answer()
    await start_command(callback.message)

# ========== ФУНКЦИИ ==========
@dp.message(F.text == "🖼 Фото")
async def photo_info(message: Message):
    balance = get_user_balance(message.from_user.id)
    await message.answer(
        "🖼 <b>Оживление фото</b>\n\n"
        "Загрузите фото → получите анимацию!\n\n"
        f"💎 Стоимость: 5 токенов\n"
        f"💰 Ваш баланс: {balance} токенов"
    )

@dp.message(F.text == "📸 Генерация")
async def generate_info(message: Message):
    balance = get_user_balance(message.from_user.id)
    await message.answer(
        "📸 <b>Генерация фото</b>\n\n"
        "Опишите что хотите → AI создаст!\n\n"
        f"💎 Стоимость: 3 токена\n"
        f"💰 Ваш баланс: {balance} токенов\n\n"
        "📝 Напишите описание:"
    )

@dp.message(F.text == "🎥 Видео")
async def video_info(message: Message):
    balance = get_user_balance(message.from_user.id)
    await message.answer(
        "🎥 <b>Видео</b>\n\n"
        "Создам видео по сценарию!\n\n"
        f"💎 Стоимость: 10 токенов\n"
        f"💰 Ваш баланс: {balance} токенов"
    )

@dp.message(F.text == "🗣 Озвучка")
async def voice_info(message: Message):
    balance = get_user_balance(message.from_user.id)
    await message.answer(
        "🗣 <b>Озвучка</b>\n\n"
        "Текст в речь!\n\n"
        f"💎 Стоимость: 1 токен/100 символов\n"
        f"💰 Ваш баланс: {balance} токенов"
    )

@dp.message(F.text == "🧠 Чат")
async def chat_info(message: Message):
    balance = get_user_balance(message.from_user.id)
    await message.answer(
        "🧠 <b>Чат</b>\n\n"
        "Общайтесь с AI!\n\n"
        f"💎 Стоимость: 1 токен/запрос\n"
        f"💰 Ваш баланс: {balance} токенов\n\n"
        "💬 Напишите вопрос:"
    )

# ========== 👑 АДМИН-ПАНЕЛЬ ==========
@dp.message(Command("stats"))
async def stats_command(message: Message):
    """Показывает статистику только админу"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Эта команда только для администратора!")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_refresh_stats")],
        [InlineKeyboardButton(text="📤 Экспорт пользователей", callback_data="admin_export_users")]
    ])
    
    await message.answer(get_stats_text(), reply_markup=keyboard)

@dp.message(F.text == "📊 Статистика")
async def admin_stats(message: Message):
    """Кнопка статистики для админа"""
    if message.from_user.id != ADMIN_ID:
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_refresh_stats")],
        [InlineKeyboardButton(text="📤 Экспорт пользователей", callback_data="admin_export_users")]
    ])
    
    await message.answer(get_stats_text(), reply_markup=keyboard)

@dp.callback_query(F.data == "admin_refresh_stats")
async def refresh_stats(callback: CallbackQuery):
    """Обновление статистики"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Недостаточно прав", show_alert=True)
        return
    
    await callback.answer("🔄 Статистика обновлена!")
    await callback.message.edit_text(get_stats_text(), reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_refresh_stats")],
            [InlineKeyboardButton(text="📤 Экспорт пользователей", callback_data="admin_export_users")]
        ]
    ))

@dp.callback_query(F.data == "admin_export_users")
async def export_users(callback: CallbackQuery):
    """Экспорт списка пользователей"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Недостаточно прав", show_alert=True)
        return
    
    users_list = "\n".join([f"• <code>{uid}</code>" for uid in list(user_stats["registered_users"])[:20]])
    total = user_stats["total_users"]
    
    text = f"📤 <b>Список пользователей (первые 20 из {total})</b>\n\n{users_list}"
    await callback.message.answer(text)

# ========== 👑 ПЕРЕСЫЛКА СООБЩЕНИЙ АДМИНУ ==========
@dp.message()
async def forward_to_admin(message: Message):
    """Пересылает все сообщения пользователей админу"""
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID:
        return
    
    # Информация о пользователе
    user_info = (
        f"👤 <b>Пользователь:</b> {message.from_user.first_name}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"⏱ <b>Время:</b> {message.date.strftime('%d.%m.%Y %H:%M')}"
    )
    if message.from_user.username:
        user_info += f"\n📱 <b>Username:</b> @{message.from_user.username}"
    
    try:
        if message.text:
            await bot.send_message(
                ADMIN_ID,
                f"{user_info}\n\n💬 <b>Сообщение:</b>\n{message.text}"
            )
            await message.answer("✅ Ваше сообщение отправлено администратору!")
        
        elif message.photo:
            await bot.send_photo(
                ADMIN_ID,
                message.photo[-1].file_id,
                caption=f"{user_info}\n\n🖼 <b>Фото</b>"
            )
            await message.answer("✅ Фото отправлено администратору!")
        
        elif message.video:
            await bot.send_video(
                ADMIN_ID,
                message.video.file_id,
                caption=f"{user_info}\n\n🎥 <b>Видео</b>"
            )
            await message.answer("✅ Видео отправлено администратору!")
        
        elif message.document:
            await bot.send_document(
                ADMIN_ID,
                message.document.file_id,
                caption=f"{user_info}\n\n📄 <b>Документ</b>"
            )
            await message.answer("✅ Документ отправлен администратору!")
            
    except Exception as e:
        logger.error(f"❌ Ошибка пересылки: {e}")

@dp.message(F.reply_to_message)
async def reply_to_user(message: Message):
    """Ответ админа пользователю"""
    if message.from_user.id != ADMIN_ID:
        return
    
    reply_text = message.reply_to_message.text or message.reply_to_message.caption or ""
    match = re.search(r'🆔 ID:.*?(\d+)', reply_text)
    
    if match:
        user_id = int(match.group(1))
        try:
            await bot.send_message(
                user_id,
                f"📨 <b>Ответ администратора:</b>\n\n{message.text}"
            )
            await message.answer("✅ Ответ отправлен пользователю!")
            logger.info(f"✅ Ответ отправлен пользователю {user_id}")
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
    else:
        await message.answer("❌ Не удалось найти ID пользователя")

# ========== ПОДДЕРЖКА ==========
@dp.message(Command("support"))
async def support_command(message: Message):
    await message.answer(
        "🛠 <b>Поддержка</b>\n\n"
        "📧 Напишите ваше сообщение, и мы ответим вам в ближайшее время!\n\n"
        "✅ Обычное время ответа: 5-15 минут"
    )

# ========== ПОМОЩЬ ==========
@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "❓ <b>Помощь</b>\n\n"
        "🚀 /start - Запуск бота\n"
        "📋 /menu - Главное меню\n"
        "👤 /profile - Мой профиль\n"
        "💎 /buy - Купить токены\n"
        "💰 /balance - Мой баланс\n"
        "🛠 /support - Связаться с поддержкой\n\n"
        "🟦 Нажми на синюю кнопку ☰ в левом нижнем углу"
    )

# ========== ЗАПУСК БОТА ==========
async def main():
    logger.info("=" * 60)
    logger.info("🚀 ЗАПУСК БОТА NOVA AI СО СТАТИСТИКОЙ")
    logger.info("=" * 60)
    
    bot_info = await bot.get_me()
    logger.info(f"🤖 Бот: @{bot_info.username}")
    logger.info(f"👑 Админ ID: {ADMIN_ID}")
    
    # Устанавливаем команды для синего меню
    commands = [
        types.BotCommand(command="start", description="🚀 Запуск"),
        types.BotCommand(command="menu", description="📋 Меню"),
        types.BotCommand(command="profile", description="👤 Профиль"),
        types.BotCommand(command="buy", description="💎 Токены"),
        types.BotCommand(command="balance", description="💰 Баланс"),
        types.BotCommand(command="support", description="🛠 Поддержка"),
        types.BotCommand(command="help", description="❓ Помощь"),
        types.BotCommand(command="stats", description="📊 Статистика"),
    ]
    await bot.set_my_commands(commands)
    logger.info("✅ Синее меню установлено")
    
    # Удаляем вебхук и запускаем
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"🚨 Фатальная ошибка: {e}")
        import traceback
        traceback.print_exc()