import subprocess
import sys

if __name__ == "__main__":
    print("🚀 Запускаем Telegram бота...")
    # Просто запускаем bot.py
    result = subprocess.run([sys.executable, "bot.py"])
    print(f"Бот завершился с кодом: {result.returncode}")
