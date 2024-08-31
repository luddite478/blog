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


@app.route('/audio/<filename>')
def stream_audio(filename):
    try:
        data = minioClient.get_object(bucket_name, filename)
        return Response(data, mimetype='audio/mpeg')
    except S3Error as err:
        return str(err)

@app.route('/create_post', methods=['POST'])
def create_post():
    # Ensure the request is JSON
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    post_data = request.get_json()

    # Insert the post data into the MongoDB collection
    try:
        result = db.posts.insert_one(post_data)
        return jsonify({"message": "Post created", "post_id": str(result.inserted_id)}), 201
    except Exception as e:
        logging.error(f"Error inserting post into MongoDB: {e}")
        return jsonify({"error": "Error creating post"}), 500


def get_posts():
    # Connect to the MongoDB client
    client = MongoClient('mongodb://localhost:27017/')
    
    # Select the database
    db = client['mydatabase']
    
    # Select the collection
    posts_collection = db['posts']
    
    # Query all documents in the collection
    posts = posts_collection.find({})
    
    # Convert the query result to a list
    posts_list = list(posts)
    
    # Close the MongoDB connection
    client.close()
    
    return posts_list

