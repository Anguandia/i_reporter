from flask import jsonify, make_response
from app.routes import app


@app.errorhandler(400)
def bad_request(error):
    return make_response(
      jsonify({'Status': 400, 'error': 'empty request'}), 400
      )
