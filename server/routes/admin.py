import os
from flask import Flask, Response, render_template
from minio import Minio
from minio.error import S3Error
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask import Blueprint, render_template
from scripts.get_posts import get_posts

admin = Blueprint('admin', __name__)

logging.basicConfig(level=logging.ERROR)

@admin.route('/')
def admin_page():
    posts = get_posts()
    response_posts = []
    for post in posts:
        try:
            post_data = {
                "date": post['date'] if 'date' in post else '',
                "audio": post['audio'] if 'audio' in post else [],
                "words": post['words'] if 'words' in post else '',
                "title": post['title'] if 'title' in post else ''
            }

            response_posts.append(post_data)
        except ValueError as e:
            logging.error(f"Error processing post: {e}")
            return jsonify({"error": "Error processing post"}), 500
    
    response_posts.sort(key=lambda x: x['date'], reverse=True)

    # Render the template 
    rendered_template = render_template('admin.html', posts=response_posts)
    
    # Print the rendered template
    # print(rendered_template)
    
    return rendered_template