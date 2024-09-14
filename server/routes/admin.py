import os
from flask import Flask, Response, render_template
from minio import Minio
from minio.error import S3Error
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask import Blueprint, render_template
from scripts.get_posts import get_posts
from babel.dates import format_date
from flask_babel import Babel

# logging.basicConfig(level=logging.DEBUG)
# print = logging.debug/
logging.getLogger('pymongo').setLevel(logging.WARNING)

admin = Blueprint('admin', __name__)

# Initialize Babel
app = Flask(__name__)
babel = Babel(app)

@babel.localeselector
def get_locale():
    # You can use request.accept_languages to get the best match for the user's language
    return request.accept_languages.best_match(['en', 'es', 'fr', 'de', 'zh'])

@admin.route('/')
def admin_page():
    posts = get_posts()
    
    # Sort posts by date in descending order before processing
    posts.sort(key=lambda x: x['date'], reverse=True)
    
    response_posts = []
    for post in posts:
        try:
            post_data = {
                "id": str(post['_id']) if '_id' in post else '',
                "date": format_date(post['date'], format='long', locale=get_locale()) if 'date' in post else '',
                "blocks": post['blocks'] if 'blocks' in post else [],
                "title": post['title'] if 'title' in post else ''
            }

            response_posts.append(post_data)
        except ValueError as e:
            print(f"Error processing post: {e}")
            return jsonify({"error": "Error processing post"}), 500
    
    # Render the template 
    rendered_template = render_template('admin.html', posts=response_posts)
    
    # Print the rendered template
    # print(rendered_template)
    
    return rendered_template