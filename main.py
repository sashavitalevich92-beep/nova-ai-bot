from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '✅ Bot is running on Timeweb!'

@app.route('/health')
def health():
    return 'OK', 200

# Только Flask app, без app.run()!
