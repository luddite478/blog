import os
from flask import Flask, Response, render_template
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask import Blueprint, render_template
from scripts.get_posts import get_posts

home = Blueprint('home', __name__)

load_dotenv()

@home.route('/')
def home_page():
    posts = get_posts()
    
    # Sort posts by date in descending order before processing
    posts.sort(key=lambda x: x['date'], reverse=True)
    
    response_posts = []
    for post in posts:
        try:
            post_data = {
                "id": str(post['_id']) if '_id' in post else '',
                "date": post['date'].strftime('%B %d, %Y') if 'date' in post else '',
                "blocks": post['blocks'] if 'blocks' in post else [],
                "title": post['title'] if 'title' in post else ''
            }

            response_posts.append(post_data)
        except ValueError as e:
            print(f"Error processing post: {e}")
            return jsonify({"error": "Error processing post"}), 500
    
    # Render the template 
    rendered_template = render_template('home.html', posts=response_posts)
        
    return rendered_template