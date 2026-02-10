import multiprocessing

# Количество воркеров
workers = 1
worker_class = 'sync'

# Порт
bind = '0.0.0.0:5000'

# Логирование
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Перезапуск при ошибках
max_requests = 1000
max_requests_jitter = 50

# Таймауты
timeout = 60
keepalive = 5
