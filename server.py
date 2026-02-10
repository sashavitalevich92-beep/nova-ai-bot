from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import sys
import os

sys.path.append(os.path.dirname(__file__))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Отключаем логи

def run_server():
    server = HTTPServer(('0.0.0.0', 8080), Handler)
    server.serve_forever()

if __name__ == '__main__':
    # Запускаем бота
    try:
        import bot
        bot_thread = threading.Thread(target=bot.main, daemon=True)
        bot_thread.start()
        print("✅ Бот запущен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Запускаем health check сервер
    run_server()
