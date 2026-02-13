import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from yookassa import Configuration, Payment
import uuid

app = FastAPI()

# ========== ТВОИ РЕАЛЬНЫЕ КЛЮЧИ (ВСТАВЬ ИХ!) ==========
Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")
# =====================================================

@app.get('/')
async def root():
    return {"message": "ЮKassa сервер работает!"}

@app.get('/create_payment/{amount}')
async def create_payment(amount: float):
    try:
        payment = Payment.create({
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "http://127.0.0.1:8000/success"
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
        return {"error": str(e)}

@app.get('/payment/{payment_id}')
async def get_payment(payment_id: str):
    try:
        payment = Payment.find_one(payment_id)
        return {"status": payment.status}
    except Exception as e:
        return {"error": str(e)}

@app.get('/success')
async def success():
    return {"message": "Оплата успешна!"}