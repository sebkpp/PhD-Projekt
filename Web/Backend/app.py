from flask import Flask
from flask_cors import CORS
from routes import register_routes
from cleanup import start_cleanup_thread

app = Flask(__name__)
CORS(app)
register_routes(app)
start_cleanup_thread()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)