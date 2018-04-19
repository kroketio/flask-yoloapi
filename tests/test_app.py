# test_app.py
import sys
import json
import pytest
from flask import url_for

mimetype = 'application/json'
headers = {
    'Content-Type': mimetype,
    'Accept': mimetype
}


class TestApp:
    def test_api_get(self, client):
        data = {'name': 'test'}
        res = client.get(url_for("api_test_get"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 200
        assert res.json == {'data': 'test'}

    def test_api_get_required(self, client):
        data = {}
        res = client.get(url_for("api_test_get"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 500
        assert 'argument \'name\' is required' in res.json.get('data')

    def test_api_get_coerce(self, client):
        data = {'name': 'test', 'age': '28'}
        res = client.get(url_for("api_test_get_coerce"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 200
        assert res.json == {'data': ['test', 28]}

        data = {'name': 'test', 'age': 'error'}
        res = client.get(url_for("api_test_get_coerce"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 500
        assert 'wrong type for argument \'age\'' in res.json.get('data')

    def test_api_any(self, client):
        data = {'name': 42}
        res = client.get(url_for("api_test_any"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 200
        assert res.json == {'data': '42'}

    def test_api_post(self, client):
        data = {'name': 'test'}
        res = client.post(url_for("api_test_post"), data=json.dumps(data), headers=headers)
        assert res.content_type == mimetype
        assert res.status_code == 200
        assert res.json == {'data': 'test'}

    def test_api_get_defaults(self, client):
        res = client.get(url_for("api_test_get_default"))
        assert res.content_type == mimetype
        assert res.status_code == 200
        assert res.json == {'data': 'default'}

    def test_api_datetime(self, client):
        data = {'date': '2018-01-01'}
        res = client.get(url_for("api_test_datetime"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 200
        assert res.json == {'data': 'Mon, 01 Jan 2018 00:00:00 GMT'}

        data = {'date': 'error'}
        res = client.get(url_for("api_test_datetime"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 500
        assert 'datetime \'date\' could not be parsed' in res.json.get('data')

    def test_api_bool(self, client):
        data = {'flag': 'true'}
        res = client.get(url_for("api_test_bool"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 200
        assert res.json == {'data': True}

        data = {'flag': 'y'}
        res = client.get(url_for("api_test_bool"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 200
        assert res.json == {'data': True}

        data = {'flag': 'N'}
        res = client.get(url_for("api_test_bool"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 200
        assert res.json == {'data': False}

        data = {'flag': 'NOPE'}
        res = client.get(url_for("api_test_bool"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 500
        assert 'wrong type for argument \'flag\'' in res.json.get('data')

        data = {'flag': ['error']}
        res = client.post(url_for("api_test_bool"), data=json.dumps(data), headers=headers)
        assert res.content_type == mimetype
        assert res.status_code == 500
        assert 'wrong type for argument \'flag\'' in res.json.get('data')

    def test_api_age_validator(self, client):
        data = {'age': 20}
        res = client.get(url_for("api_test_age_validator"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 200
        assert res.json == {'data': 20}

        # custom Flask.Response returns from within the validator
        data = {'age': 120}
        res = client.get(url_for("api_test_age_validator"), query_string=data)
        assert res.status_code == 403
        if isinstance(res.data, bytes):
            data = res.data.decode('utf8')
        assert 'all lies' in data

        # trigger exception from within the validator
        data = {'age': 150}
        res = client.get(url_for("api_test_age_validator"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 500
        assert "parameter 'age' error: you can't possibly be that old!" in res.json.get('data')

        # test invalid response
        data = {'age': 110}
        res = client.get(url_for("api_test_age_validator"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 500
        assert "validator returned an unknown format" in res.json.get('data')

    def test_api_broken_route(self, client):
        data = {'age': 28}
        res = client.get(url_for("api_test_broken_route"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 500
        assert res.json == {'data': 'whoops', 'docstring': None}

    def test_api_status_code(self, client):
        data = {'age': 28}
        res = client.get(url_for("api_test_status_code"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 203
        assert res.json == {'data': '203 test'}

    def test_api_bad_status_code(self, client):
        data = {'age': 28}
        res = client.get(url_for("api_test_bad_status_code"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 500
        assert "when returning tuples, the first index must be an object of" in res.json.get('data')

    def test_api_unknown_return(self, client):
        try:
            res = client.get(url_for("api_test_unknown_return"), query_string={'age': 28})
        except Exception as ex:
            assert isinstance(ex, TypeError)
            assert 'Bad return type' in str(ex)

    def test_api_empty_return(self, client):
        res = client.get(url_for("api_test_empty_return"))
        assert res.status_code == 204

    def test_api_custom_return(self, client):
        res = client.get(url_for("api_test_custom_return"))
        assert res.status_code == 203

    def test_api_docstring(self, client):
        # tests auto docstring generation
        res = client.get(url_for("api_test_docstring"), query_string={'foo': 'whoop'})
        assert res.status_code == 500
        assert res.json == {
            'data': 'whoops',
            'docstring': {
                'return': 'Nothing, really.',
                'params': {
                    'foo': {'required': False, 'help': 'bar!', 'type': 'str'}},
                'help': 'Just a test. With multiple lines.'
            }
        }

    def test_api_types(self, client):
        # first test GET
        res = client.get(url_for("api_test_types"), query_string={
            'a': 'test',
            'b': 2,
            'e': '2018-01-02'
        })
        assert res.content_type == mimetype
        assert res.status_code == 200
        assert res.json == {'data': ['test', 2, None, None, 'Tue, 02 Jan 2018 00:00:00 GMT', None]}

        # test POST, include dict and list
        res = client.post(url_for("api_test_types"), data=json.dumps({
            'a': 'test',
            'b': 2,
            'c': {'foo': 'bar'},
            'd': ['foo', 'bar'],
            'e': '2018-01-02',
            'f': False
        }), headers=headers)
        assert res.status_code == 200
        assert res.content_type == mimetype
        assert res.json == {'data': ['test', 2, {'foo': 'bar'}, ['foo', 'bar'], 'Tue, 02 Jan 2018 00:00:00 GMT', False]}

    def test_api_type_annotations(self, client):
        if not sys.version_info >= (3, 5):  # python >= 3.5 only
            return

        data = {'name': 'sander', 'age': 28}
        res = client.get(url_for("api_test_type_annotations"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 200
        assert res.json == {'data': {'name': 'sander', 'location': 'Amsterdam', 'age': 28}}

        data = {'name': 'sander', 'age': 28}
        res = client.get(url_for("api_test_type_annotations_fail"), query_string=data)
        assert res.content_type == mimetype
        assert res.status_code == 500
        assert 'no type specified for parameter \'age\'' in res.json.get('data')

    def test_yolo_decorator(self, client):
        from flask_yoloapi import endpoint, parameter
        exceptions = 0

        try:
            @client.application.route('/bad_parameter_key')
            @endpoint.api(
                parameter(1, type=int, required=True)
            )
            def bad_parameter_key():
                pass
        except Exception as ex:
            exceptions += 1
            assert isinstance(ex, TypeError)
            assert 'bad type for \'key\'; must be' in str(ex)

        assert exceptions == 1

        try:
            @client.application.route('/bad_parameter_required')
            @endpoint.api(
                parameter('foo', type=str, required=1)
            )
            def bad_parameter_required(foo):
                pass
        except Exception as ex:
            exceptions += 1
            assert isinstance(ex, TypeError)
            assert 'bad type for \'required\'; must be' in str(ex)

        assert exceptions == 2

        try:
            @client.application.route('/bad_parameter_required')
            @endpoint.api(
                parameter('foo', type=str, validator=1)
            )
            def bad_parameter_validator(foo):
                pass
        except Exception as ex:
            exceptions += 1
            assert isinstance(ex, TypeError)
            assert 'parameter \'validator\' must be a function' in str(ex)

        assert exceptions == 3

        try:
            @client.application.route('/bad_parameter_type')
            @endpoint.api(
                parameter('foo', type=FileExistsError, validator=1)
            )
            def bad_parameter_type(foo):
                pass
        except Exception as ex:
            exceptions += 1
            assert isinstance(ex, TypeError)
            assert 'not supported' in str(ex)

        assert exceptions == 4

        try:
            @client.application.route('/bad_parameter_location')
            @endpoint.api(
                parameter('foo', type=int, location='error')
            )
            def bad_parameter_location(foo):
                pass
        except Exception as ex:
            exceptions += 1
            assert isinstance(ex, ValueError)
            assert 'unknown location' in str(ex)

        assert exceptions == 5

        try:
            @client.application.route('/bad_parameter_bad_default')
            @endpoint.api(
                parameter('foo', type=str, default=int)
            )
            def bad_parameter_bad_default(foo):
                pass
        except TypeError as ex:
            exceptions += 1
            assert isinstance(ex, TypeError)
            assert 'not supported' in str(ex)

        assert exceptions == 6