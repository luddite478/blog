import os
from flask import Flask, request, jsonify
from minio import Minio
from minio.error import S3Error
import logging
from dotenv import load_dotenv
from flask import Blueprint, render_template
from scripts.get_posts import get_posts
from datetime import datetime
from pymongo import MongoClient

api = Blueprint('api', __name__)

logging.basicConfig(level=logging.ERROR)

app = Flask(__name__)
minioClient = Minio(
    os.environ.get("MINIO_ENDPOINT"),
    access_key=os.environ.get("MINIO_ROOT_USER"),
    secret_key=os.environ.get("MINIO_ROOT_PASSWORD"),
    secure=False
)

MINIO_BUCKET_NAME = "audio"

try:
    MONGO_URI = os.environ.get('MONGO_URI')
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client['blog']
    
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")
    raise

def upload_files_to_minio(files):
    file_urls = []
    for file in files:
        try:
            # Upload the file to MinIO
            minioClient.put_object(
                MINIO_BUCKET_NAME,
                file.filename,
                file.stream,
                length=-1,  # Automatically calculate the length
                part_size=10*1024*1024  # 10 MB part size
            )
            file_url = f"{os.environ.get('MINIO_ENDPOINT')}/{MINIO_BUCKET_NAME}/{file.filename}"
            file_urls.append(file_url)
        except Exception as e:
            logging.error(f"Error uploading file to MinIO: {e}")
            raise
    return file_urls

@app.route('/create_post', methods=['POST'])
def create_post():
        
    # Ensure the request contains form data
    if not request.form:
        return jsonify({"error": "Request must contain form data"}), 400

    # Extract form data
    title = request.form.get('title')
    words = request.form.get('words')
    files = request.files.getlist('files')

    if not words or not files:
        return jsonify({"error": "Missing required form data"}), 400

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        file_urls = upload_files_to_minio(files)
    except Exception as e:
        return jsonify({"error": "Error uploading files"}), 500

    post_data = {
        "title": title,
        "date": date,
        "words": words,
        "file_urls": file_urls 
    }

    try:
        result = db.posts.insert_one(post_data)
        return jsonify({"message": "Post created", "post_id": str(result.inserted_id)}), 201
    except Exception as e:
        logging.error(f"Error inserting post into MongoDB: {e}")
        return jsonify({"error": "Error creating post"}), 500
    