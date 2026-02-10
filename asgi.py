from main import app
from hypercorn.asyncio import serve
from hypercorn.config import Config
import asyncio

# онвертируем Flask в ASGI
asgi_app = app

if __name__ == "__main__":
    config = Config()
    config.bind = ["0.0.0.0:8000"]
    asyncio.run(serve(asgi_app, config))
