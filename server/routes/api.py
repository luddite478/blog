import os
import random
from flask import Flask, request, jsonify
from minio import Minio
import logging
from minio.error import S3Error
from dotenv import load_dotenv
from flask import Blueprint, render_template
from scripts.posts import get_posts
from scripts.delete_posts import delete_posts_by_ids
from scripts.audio_convertion import convert_to_mp3
from datetime import datetime, timedelta
from pymongo import MongoClient
import uuid
import tempfile

api = Blueprint('api', __name__)
##########
'''
pip install flask-cors
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://your-admin-page.com"}})
from functools import wraps
from flask import request, jsonify

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token != os.environ.get('ADMIN_TOKEN'):
            return jsonify({"error": "Unauthorized access"}), 403
        return f(*args, **kwargs)
    return decorated_function
    from functools import wraps
from flask import request, jsonify

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token != os.environ.get('ADMIN_TOKEN'):
            return jsonify({"error": "Unauthorized access"}), 403
        return f(*args, **kwargs)
    return decorated_function
    
@api.route('/create-post', methods=['POST'])
@admin_required
def create_post():
'''
##########
def initialize_minio_client():
    return Minio(
        os.environ.get("MINIO_INTERNAL_ADDRESS"),
        access_key=os.environ.get("MINIO_ACCESS_KEY"),
        secret_key=os.environ.get("MINIO_SECRET_KEY"),
        secure=False
    )

minioClient = initialize_minio_client()

logging.getLogger('pymongo').setLevel(logging.WARNING)

ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'flac', 'aac', 'ogg'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

def initialize_mongo_client():
    try:
        MONGO_URI = os.environ.get('MONGO_URI')
        mongo_client = MongoClient(MONGO_URI)
        return mongo_client['blog']
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

db = initialize_mongo_client()

def upload_file_stream_to_minio(file, filename, bucket):
    MINIO_PROTOCOL = 'http'
    try:
        minioClient.put_object(
            bucket,
            filename,
            file.stream,
            length=-1,  # Automatically calculate the length
            part_size=10*1024*1024  # 10 MB part size
        )
        file_url = f"{MINIO_PROTOCOL}://{os.environ.get('MINIO_PUBLIC_ADDRESS')}/{bucket}/{filename}"
        return file_url
    except Exception as e:
        print(f"Error uploading file to MinIO: {e}")
        raise

def upload_file_to_minio(file_path, filename, bucket):
    MINIO_PROTOCOL = 'http'
    try:
        with open(file_path, 'rb') as f:
            file_stat = os.stat(file_path)
            minioClient.put_object(
                bucket,
                filename,
                f,
                length=file_stat.st_size,
                part_size=10*1024*1024  # 10 MB part size
            )

        file_url = f"{MINIO_PROTOCOL}://{os.environ.get('MINIO_PUBLIC_ADDRESS')}/{bucket}/{filename}"
        return file_url
    except Exception as e:
        print(f"Error uploading file to MinIO: {e}")
        raise

def validate_audio_file(audio_block):
    file_extension = audio_block['filename'].filename.rsplit('.', 1)[1].lower()
    if file_extension not in ALLOWED_AUDIO_EXTENSIONS:
        return None

def handle_form_data(form_data):
    post_data = {
        "date": datetime.now(),
        "title": form_data.get('title', '')
    }
    blocks = []

    if 'words' in form_data:
        file_id = str(uuid.uuid4())[:6]
        blocks.append({
            'id': file_id,
            'type': 'words',
            'text': form_data['words']
        })

    return post_data, blocks

def handle_audio_file(f, file_id, file_extension):
    filename = f'{file_id}.{file_extension}'
    files = [
        {
            "extension": file_extension,
            "s3_path": upload_file_stream_to_minio(f, filename, 'audio')
        }
    ]

    if file_extension != 'mp3':
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp:
                f.seek(0)  # Ensure the file stream is reset before saving
                f.save(tmp.name)
                print(f'Temporary file saved at: {tmp.name}')
                print(f'Temporary file size: {os.path.getsize(tmp.name)} bytes')

            # Convert saved temp file to mp3
            mp3_file_path = convert_to_mp3(tmp.name)
            filename = f'{file_id}.mp3'
            files.append({
                "extension": 'mp3',
                "s3_path": upload_file_to_minio(mp3_file_path, filename, 'audio')
            })

        except Exception as e:
            print(f"Error saving or converting the temporary file: {e}")
            raise

    return {
        "type": "audio",
        "files": files,
        "file_id": file_id,
        "original_name": f.filename
    }

def handle_video_file(f, file_id, file_extension):
    filename = f'{file_id}.{file_extension}'
    files = [{
        "extension": file_extension,
        "s3_path": upload_file_stream_to_minio(f, filename, 'video')
    }]
    return {
        "type": "video",
        "files": files,
        "file_id": file_id,
        "original_name": f.filename
    }

@api.route('/create-post', methods=['POST'])
def create_post():
    try:
        if not request.form:
            return jsonify({"error": "Request must contain form data"}), 400

        form_data = request.form.to_dict()
        print('Form Data:', form_data)
        
        files_data = {key: file.filename for key, file in request.files.items()}
        print('Files:', files_data)

        post_data, blocks = handle_form_data(form_data)

        for _, f in request.files.items():
            if f.filename == '':
                return "No selected file", 400              
            file_id = str(uuid.uuid4())[:6]
            file_extension = f.filename.rsplit('.', 1)[1].lower()
            print(f"File received: {f.filename}, size: {len(f.read())} bytes")
            f.seek(0)  # Reset stream position after read
            if file_extension in ALLOWED_AUDIO_EXTENSIONS:
                blocks.append(handle_audio_file(f, file_id, file_extension))
            elif file_extension in ALLOWED_VIDEO_EXTENSIONS:
                blocks.append(handle_video_file(f, file_id, file_extension))

        post_data['blocks'] = blocks

        result = db.posts.insert_one(post_data)
        return jsonify({"message": "Post created", "post_id": str(result.inserted_id)}), 201
    
    except Exception as e:
        print(f"Internal server error: {e}")
        return jsonify({"error": "Error creating post"}), 500

@api.route('/delete-posts', methods=['DELETE'])
def delete_posts():
    try:
        if not request.json or 'ids' not in request.json:
            return jsonify({"error": "Request must contain JSON data with 'ids'"}), 400

        ids = request.json['ids']
        delete_posts_by_ids(ids)
        return jsonify({"message": "Posts deleted"}), 200
    
    except Exception as e:
        print(f"Internal server error: {e}")
        return jsonify({"error": "Error deleting posts"}), 500