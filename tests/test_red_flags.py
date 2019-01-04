import os
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


# Test correct generation of flag id
def test_generate_unique_and_sequential_flag_ids(client):
    # create a 100 flags
    [post_json(client, 'api/v1/red_flags', dat['basic']) for i in range(100)]
    response = client.get('/api/v1/red_flags')
    # extract the flags list from the getall response
    message = json_of_response(response)['data']
    # generate a list of all flag ids
    ids = [flag['id'] for flag in message]
    # check that ids are unique
    assert len(set(ids)) == len(ids)
    # check that ids are sequential(auto-increamenting)
    assert ids == list(range(1, 101))


# Test optional fields set during creation if supplied
def test_optional_flag_properties_set_in_creation(client):
    post_json(client, '/api/v1/red_flags', dat['optional'])
    response = client.get('/api/v1/red_flags/1')
    assert json_of_response(response)['data'][0]['type'] == 'intervention flag'


# Test can retrieve all red_flags; correct response code and body
def test_get_flags(client):
    post_json(client, '/api/v1/red_flags', dat['basic'])
    post_json(client, '/api/v1/red_flags', dat['basic'])
    post_json(client, '/api/v1/red_flags', dat['basic'])
    post_json(client, '/api/v1/red_flags', dat['basic'])
    response = client.get('/api/v1/red_flags')
    assert len(json_of_response(response)['data']) == 4


# Test correct response to get all request if none; code and body
def test_get_all_fails_when_none(client):
    response = client.get('/api/v1/red_flags')
    assert response.status_code == 404
    assert json_of_response(response) == {
            'Status': 404, 'error': 'no red flags'
            }


# Test can fetch particular flag by id; correct response code and body
def test_get_single_flag_by_id(client):
    flag = post_json(client, '/api/v1/red_flags', {
            'location': 'there', 'createdBy': 10, 'comment': 'gavi money'
            })
    assert json_of_response(flag)['Status'] == 201
    resp = client.get('/api/v1/red_flags/1')
    assert json_of_response(resp)['data'][0]['comment'] == 'gavi money'


# Test correct response if particular flag non available
def test_get_single_flag_by_non_existent_id_fails(client):
    resp = client.get('/api/v1/red_flags/100')
    assert resp.status_code == 404
    assert 'error' in json_of_response(resp)
    assert json_of_response(resp)['error'] == 'red flag not found'


# Test can edit comment
def test_can_edit_comment(client):
    post_json(client, '/api/v1/red_flags', dat['basic'])
    response = patch_json(client, '/api/v1/red_flags/1/comment', {
            'comment': 'teacher\'s salaries eaten'})
    assert json_of_response(response)['data'][0]['message'] ==\
        "updated red-flag record's comment"


# Test edit rejected if flag resolved or rejected
def test_cant_edit_resolved_flag(client):
    post_json(client, '/api/v1/red_flags', dat['resolved'])
    response = patch_json(client, '/api/v1/red_flags/1/comment', {
            'comment': 'teacher\'s salaries eaten'})
    assert json_of_response(response)['error'] == 'red flag already resolved'


# Test geolocation added to flag
def test_add_goeloc(client):
    # create record without geolocation details
    post_json(client, '/api/v1/red_flags', dat['basic'])
    # add geolocation
    resp = patch_json(
            client, '/api/v1/red_flags/1/location',
            {'location': '03.2356 31.6524'}
            )
    # check that geoloc added
    assert json_of_response(resp)['data'][0]['message'] ==\
        "added red-flag record's location"
    # modify geoloc
    patch_json(client, '/api/v1/red_flags/1/location', {
            'location': '0.000 0.000'})
    resp1 = client.get('/api/v1/red_flags/1')
    # ascertain that geoloc updated to latest value
    assert 'N: 0.000, E: 0.000' in json_of_response(resp1)['data'][0][
            'location']


# Test correct response if flag to be edited does not exist
def test_correct_response_if_flag_tobe_edited_not_exist(client):
    response = patch_json(
            client, '/api/v1/red_flags/1/comment', {'comment': 'any'}
            )
    assert json_of_response(response)['error'] == 'red flag not found'


# Test can delete given flag
def test_delete_flag(client):
    post_json(client, '/api/v1/red_flags', dat['basic'])
    response = client.delete('/api/v1/red_flags/1')
    assert json_of_response(response)['data'][0]['message'] ==\
        'red-flag record has been deleted'


# Test correct response if flag selected for deletion does not exist
def test_cant_delete_non_exitent_flag(client):
    response = client.delete('/api/v1/red_flags/1')
    assert json_of_response(response)['error'] == 'red flag not found'


'''Data validation tests to return error responses'''


# Test red_flag with missing mandatory field not created, correct error
# message in response
def test_incomplete_red_flag_not_created(client):
    response = post_json(client, 'api/v1/red_flags', dat['incomplete'])
    assert response.status_code == 400
    assert json_of_response(response)['error'] ==\
        'comment field missing, invalid key or incorrect'


# Test empty mandatory fields supplied during creation flagged,
# correct response
def test_validat_empty_required_fields_flag_not_created(client):
    response = post_json(client, '/api/v1/red_flags', dat['empty'])
    assert response.status_code == 400
    assert json_of_response(response)['error'] == 'please submit location'


# Test wrong data_type flagged in creation
def test_validate_data_types(client):
    response = post_json(client, '/api/v1/red_flags', dat['invalid'])
    assert response.status_code == 400
    assert json_of_response(response)['error'] ==\
        "createdBy should be of type <class 'int'>"


# Test correct response if new field value for edit is null
def test_cant_change_editable_field_value_to_null(client):
    post_json(client, '/api/v1/red_flags', dat['basic'])
    response = patch_json(
            client, '/api/v1/red_flags/1/comment', {'comment': ''}
            )
    assert json_of_response(response)['error'] == 'submit new comment'


# Test correct response if key for field to be edited not provided
def test_correct_response_if_key_for_field_missing(client):
    post_json(client, '/api/v1/red_flags', dat['basic'])
    response = patch_json(
            client, '/api/v1/red_flags/1/comment', {'location': 'here'}
            )
    assert json_of_response(response)['error'] ==\
        'comment key missing, check your input or url'


# Test post or patch reqquests return correct response if no data
# this tests the json_required wrapper/decorator and the error handler 400
# on all routes decorated so
def test_send_empty_request_where_data_required(client):
    result = post_json(client, '/api/v1/red_flags', '')
    assert result.status_code == 400
    assert json_of_response(result)['error'] == 'empty request'


# Test wrong endpoint flagged
def test_wrong_endpoint(client):
    result = patch_json(
            client, '/api/v1/red_flags/1/something_else', {"comment": "mihjh"}
            )
    assert result.status_code == 400
    assert json_of_response(result)['error'] ==\
        "wrong endpoint 'something_else'"


# Test wrong method for valid endpoint flagged
def test_wrong_method(client):
    res = patch_json(client, '/api/v1/red_flags/1', dat['basic'])
    assert res.status_code == 405
    assert 'wrong method' in json_of_response(res)['error']


def test_geolocation_format_checked(client):
    post_json(client, '/api/v1/red_flags', dat['basic'])
    res = patch_json(
            client, '/api/v1/red_flags/1/location', {
                    "location": "03.5623,31.5652"}
                    )
    assert res.status_code == 400
    assert 'location must be of format' in json_of_response(res)['error']


# Test wrong base url flagged
def test_wrong_base_url(client):
    res = client.get('/api/v1/wrongbase/1')
    assert 'wrong url' in json_of_response(res)['error']


# test patch request without end point flagged
def test_no_end_point_for_patch(client):
    post_json(client, '/api/v1/red_flags', dat['basic'])
    res = patch_json(client, '/api/v1/red_flags/1', {'comment': 'any'})
    assert json_of_response(res)['error'] == 'wrong method'


# Test wrong method(post) for specific red flag flaged
def test_wrong_method_post(client):
    res = post_json(client, '/api/v1/red_flags/1', dat['basic'])
    assert res.status_code == 405
    assert json_of_response(res)['error'] == 'wrong method'


# test wrong method for post/get all routes flagged
def test_wrong_method_for_post_and_get(client):
    res = client.delete('/api/v1/red_flags')
    assert json_of_response(res)['error'] == 'wrong method'


# test id type validation
def test_validate_id_type(client):
    res = client.get('/api/v1/red_flags/one')
    assert json_of_response(res)['error'] == 'id must be a number'


# Test default route
def test_default_route(client):
    res = client.get('/')
    assert 'edit flag' in json_of_response(res)


# Test correct response if wrong method for patch route
def test_correct_response_wrong_method_for_update(client):
    response = post_json(
            client, '/api/v1/red_flags/1/comment', {'comment': 'any'}
            )
    assert json_of_response(response)['error'] == 'wrong method'
