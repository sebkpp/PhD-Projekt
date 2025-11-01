from flask import Flask
from flask_cors import CORS
from Backend.routes import register_routes
from Backend.cleanup import start_cleanup_thread
from Backend.models import Base
from Backend.db_session import engine

Base.metadata.create_all(bind=engine)
app = Flask(__name__)
CORS(app)
register_routes(app)
start_cleanup_thread()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)