import subprocess
import sys
import time

print("🚀 Запускаем Telegram бота...")

# Запускаем бота как subprocess
process = subprocess.Popen([sys.executable, "bot_telegram.py"])

try:
    # Ждем
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("🛑 Останавливаем бота...")
    process.terminate()
    process.wait()
