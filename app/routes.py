import os
from flask import request, jsonify
from app import create_app
from .validation import Validation
from .implementation import Implementation


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


@app.route('/api/v1/red_flags', methods=['POST'])
def create_flag():
    data = request.json
    res = Validation().validateNew(data)
    return jsonify({'Status': res[0], res[1]: res[2]}), res[0]


@app.route('/api/v1/red_flags', methods=['get'])
def get_flags():
    res = Implementation().get_flags()
    return jsonify({'Status': res[0], res[1]: res[2]}), res[0]
