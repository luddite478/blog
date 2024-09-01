from flask import Flask
import logging
import os
from routes.home import home
from routes.admin import admin
from scripts.init_minio import init_minio

try:
    init_minio()
except Exception as e:
    logging.error(f"Error initializing MinIO: {e}")
    exit(1)

PORT = os.environ.get("ENV_TYPE", 5000)

logging.basicConfig(level=logging.DEBUG)

template_dir = os.path.abspath('./templates')
app = Flask(__name__, template_folder=template_dir)

app.register_blueprint(home, url_prefix='/')
app.register_blueprint(admin, url_prefix='/admin')

if __name__ == "__main__":
    PORT = os.environ.get("BLOG_CONTAINER_PORT", 5000)
    logging.info(f"Starting Flask server on port {PORT}")
    app.run(debug=True, host="0.0.0.0", port=PORT)