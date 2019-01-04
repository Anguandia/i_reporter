import pytest
import json
from tests.test_data import dat
from app import implementation, routes


@pytest.fixture(scope='function')
def client():
    red_flags = implementation.red_flags
    app = routes.app
    test_client = app.test_client()
    red_flags.clear()
    cxt = app.app_context()
    cxt.push()
    yield test_client
    cxt.pop()


# Encode test requests to json
def post_json(client, url, json_dict):
    return client.post(
        url, data=json.dumps(json_dict), content_type='application/json'
        )


# Decode json requests
def json_of_response(response):
    return json.loads(response.data.decode())


# Encoding for put request
def patch_json(client, url, json_dict):
    return client.patch(
            url, data=json.dumps(json_dict), content_type='application/json')


# Test red_flag creation and expected reponse; code and content
def test_red_flag_creation(client):
    response = post_json(client, 'api/v1/red_flags', dat['basic'])
    assert response.status_code == 201
    assert json_of_response(response)['data'][0]['message'] ==\
        'Created red flag'
