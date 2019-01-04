import os
from flask import request, jsonify
from app import create_app
from .validation import Validation
from .implementation import Implementation
from app.wrappers import json_required


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
@json_required
def create_flag():
    data = request.json
    res = Validation().validateNew(data)
    return jsonify({'Status': res[0], res[1]: res[2]}), res[0]


@app.route('/api/v1/red_flags', methods=['get'])
def get_flags():
    res = Implementation().get_flags()
    return jsonify({'Status': res[0], res[1]: res[2]}), res[0]


@app.route('/api/v1/red_flags/<red_flag_id>', methods=[
    'get', 'delete'])
def single_flag(red_flag_id):
    if Validation().validateId(red_flag_id):
        res = [400, 'error', Validation().validateId(red_flag_id)]
    elif request.method == 'get':
        res = Implementation().get_flag(red_flag_id)
    elif request.method == 'delete':
        res = Implementation().delete(red_flag_id)
    return jsonify({'Status': res[0], res[1]: res[2]}), res[0]


@app.route('/api/v1/red_flags/<red_flag_id>/<key>', methods=[
    'patch'])
@json_required
def edit(red_flag_id, key):
    data = request.json
    res = Validation().validateEdit(data, red_flag_id, key)
    return jsonify({'Status': res[0], res[1]: res[2]}), res[0]
