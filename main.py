import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from yookassa import Configuration, Payment
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import uuid
import logging

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NovaAI Bot API")

# ========== ЗАГРУЗКА КЛЮЧЕЙ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ==========
YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ========== НАСТРОЙКА ЮKASSA ==========
Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY

# ========== НАСТРОЙКА TELEGRAM БОТА ==========
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ========== ГЛАВНАЯ СТРАНИЦА ==========
@app.get('/')
async def root():
    return {
        "message": "✅ NovaAI Bot API работает!",
        "status": "online",
        "webhook": "/webhook",
        "docs": "/docs"
    }

# ========== ВЕБХУК ДЛЯ TELEGRAM ==========
@app.post('/webhook')
async def telegram_webhook(request: Request):
    """Принимает обновления от Telegram"""
    try:
        logger.info("📩 Получен webhook от Telegram")
        update_data = await request.json()
        logger.debug(f"Update: {update_data}")
        
        update = types.Update(**update_data)
        await dp.feed_update(bot, update)
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"❌ Ошибка webhook: {e}")
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": str(e)}
        )

# ========== ПРОВЕРКА ВЕБХУКА ==========
@app.get('/webhook')
@app.head('/webhook')
async def webhook_info():
    """Проверка доступности webhook эндпоинта"""
    return {"status": "ready", "message": "Webhook endpoint is live"}

# ========== ПРОВЕРКА ЗДОРОВЬЯ ==========
@app.get('/health')
@app.head('/health')
async def health():
    """Health check для Timeweb"""
    return {"status": "healthy"}

# ========== ПЛАТЕЖИ ==========
@app.get('/create_payment/{amount}')
async def create_payment(amount: float):
    """Создание платежа в ЮKassa"""
    try:
        # Получаем базовый URL из переменных окружения
        base_url = os.getenv("API_URL", "http://127.0.0.1:8000")
        
        payment = Payment.create({
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"{base_url}/success"
            },
            "capture": True,
            "description": f"Оплата {amount} руб"
        })
        
        return {
            "confirmation_url": payment.confirmation.confirmation_url,
            "payment_id": payment.id,
            "status": payment.status
        }
    except Exception as e:
        logger.error(f"❌ Ошибка создания платежа: {e}")
        return {"error": str(e)}

@app.get('/payment/{payment_id}')
async def get_payment(payment_id: str):
    """Проверка статуса платежа"""
    try:
        payment = Payment.find_one(payment_id)
        return {
            "payment_id": payment.id,
            "status": payment.status,
            "amount": payment.amount.value
        }
    except Exception as e:
        return {"error": str(e)}

@app.get('/success')
async def success():
    """Страница успешной оплаты"""
    return {
        "message": "✅ Оплата прошла успешно!",
        "status": "succeeded"
    }

# ========== ОТЛАДКА ==========
@app.get('/debug')
async def debug():
    """Информация о конфигурации (без секретов)"""
    try:
        webhook_info = await bot.get_webhook_info()
        return {
            "yookassa_configured": bool(YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY),
            "bot_configured": bool(BOT_TOKEN),
            "webhook_url": webhook_info.url if webhook_info else None,
            "webhook_pending": webhook_info.pending_update_count if webhook_info else 0,
            "webhook_error": webhook_info.last_error_message if webhook_info else None
        }
    except Exception as e:
        return {"error": str(e)}
