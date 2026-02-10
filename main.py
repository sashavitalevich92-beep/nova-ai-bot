from flask import Flask
import threading
import asyncio
import sys
import os
import signal
import time

# Создаем Flask приложение
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

# Функция для запуска бота
def run_bot():
    try:
        print("🚀 Импортируем бота...")
        # Динамический импорт
        import importlib.util
        spec = importlib.util.spec_from_file_location("bot", "bot_app.py")
        bot_module = importlib.util.module_from_spec(spec)
        sys.modules["bot"] = bot_module
        spec.loader.exec_module(bot_module)
        
        # Запускаем main функцию из бота
        if hasattr(bot_module, 'main'):
            print("✅ Запускаем бота...")
            asyncio.run(bot_module.main())
        else:
            print("❌ Функция main() не найдена в bot_app.py")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        import traceback
        traceback.print_exc()

# Флаг для остановки
stop_flag = False

def signal_handler(signum, frame):
    global stop_flag
    print("🛑 Получен сигнал остановки")
    stop_flag = True

if __name__ == "__main__":
    # Настраиваем обработчик сигналов
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Запускаем бота в отдельном потоке
    print("🚀 Запускаем Telegram бота в фоне...")
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Проверяем что бот запустился
    time.sleep(3)
    
    # Запускаем Flask
    print("🌐 Запускаем Flask сервер на порту 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
