from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager

app = FastAPI()

async def run_bot():
    try:
        # робуем импортировать вашего бота
        from bot import dp
        from aiogram import executor
        await executor.start_polling(dp, skip_updates=True)
    except ImportError as e:
        print(f"Bot import error: {e}")
        # аглушка если бот не найден
        while True:
            await asyncio.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # апускаем бота в фоне
    bot_task = asyncio.create_task(run_bot())
    yield
    # станавливаем при завершении
    if not bot_task.done():
        bot_task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "Bot server is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
