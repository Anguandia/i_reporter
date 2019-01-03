import os
from flask import request, jsonify
from app import create_app


config_name = os.getenv('FLASK_ENV')
app = create_app('TESTING')


@app.route('/')
@app.route('/api/v1')
@app.route('/api/v1/')
def home():
    return jsonify({
      'create or get all flags':
      '/red_flags',
      'get or delete single flag':
      '/red_flags/id',
      'edit flag': '/red_flags/id/field'
      })
