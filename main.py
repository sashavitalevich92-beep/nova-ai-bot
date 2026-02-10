from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "✅ Bot server is running!"

@app.route("/health")
def health():
    return "OK", 200

# сли у вас есть асинхронный бот, его нужно запускать отдельно
# import asyncio
# from bot import dp
# from aiogram import executor

# def run_bot():
#     asyncio.run(executor.start_polling(dp, skip_updates=True))

# if __name__ == "__main__":
#     # апускаем бот в отдельном потоке
#     import threading
#     bot_thread = threading.Thread(target=run_bot, daemon=True)
#     bot_thread.start()
#     app.run(host="0.0.0.0", port=8000)
