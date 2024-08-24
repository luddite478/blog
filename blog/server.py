import os
from flask import Flask, Response, render_template
from minio import Minio
from minio.error import S3Error
import logging

logging.basicConfig(level=logging.DEBUG)

PORT=os.environ.get("BLOG_CONTAINER_PORT")

def strip_http(url):
    return url.replace("http://", "").replace("https://", "")

app = Flask(__name__)
minioClient = Minio(
    strip_http(os.environ.get("MINIO_ENDPOINT")),
    access_key=os.environ.get("MINIO_ROOT_USER"),
    secret_key=os.environ.get("MINIO_ROOT_PASSWORD"),
    secure=False
)

bucket_name = 'audio'
if not minioClient.bucket_exists(bucket_name):
    try:
        minioClient.make_bucket(bucket_name)
    except S3Error as err:
        print(str(err))

@app.route('/')
def home():
    posts = [
        {'audio_s3_path': 'test', 'date': 'This is the first post.'},
        {'audio_s3_path': 'test', 'date': 'This is the second post.'},
    ]
    return render_template('index.html', posts=posts)

@app.route('/audio/<filename>')
def stream_audio(filename):
    try:
        data = minioClient.get_object(bucket_name, filename)
        return Response(data, mimetype='audio/mpeg')
    except S3Error as err:
        return str(err)

if __name__ == "__main__":
    logging.info(f"Starting Flask server on port {PORT}")
    app.run(debug=True, host="0.0.0.0", port=PORT)