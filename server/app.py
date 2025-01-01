from flask import Flask, request
import os
from routes.home import home
from routes.admin import admin
from routes.api import api
from scripts.init_minio import init_minio
import logging

try:
    init_minio()
except Exception as e:
    print(f"Error initializing MinIO: {e}")
    exit(1)

PORT = 80
logging.basicConfig(level=logging.DEBUG)

template_dir = os.path.abspath('./templates')
app = Flask(__name__, template_folder=template_dir)

@app.before_request
def log_request_info():
    app.logger.debug(f"Request Headers: {request.headers}")
    app.logger.debug(f"Request Body: {request.get_data()}")

app.register_blueprint(home, url_prefix='/')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(api, url_prefix='/api')

if __name__ == "__main__":
    logging.info(f"Starting Flask server on port {PORT}")
    app.run(debug=True, host="0.0.0.0", port=PORT)