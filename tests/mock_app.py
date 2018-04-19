import sys
from datetime import datetime

from flask import Flask, Response

from flask_yoloapi.types import ANY
from flask_yoloapi import endpoint, parameter


def create_app():
    app = Flask(__name__)

    @app.route('/api/test_get')
    @endpoint.api(
        parameter('name', type=str, required=True)
    )
    def api_test_get(name):
        return name

    @app.route('/api/test_get_coerce')
    @endpoint.api(
        parameter('name', type=str, required=True),
        parameter('age', type=int, required=True)
    )
    def api_test_get_coerce(name, age):
        return [name, age]

    @app.route('/api/test_any')
    @endpoint.api(
        parameter('name', type=ANY, required=True)
    )
    def api_test_any(name):
        return name

    @app.route('/api/test_post', methods=['POST'])
    @endpoint.api(
        parameter('name', type=str)
    )
    def api_test_post(name):
        return name

    @app.route('/api/test_get_default')
    @endpoint.api(
        parameter('name', type=str, default='default')
    )
    def api_test_get_default(name):
        return name

    @app.route('/api/test_datetime')
    @endpoint.api(
        parameter('date', type=datetime, required=True)
    )
    def api_test_datetime(date):
        return date

    @app.route('/api/test_bool', methods=['GET', 'POST'])
    @endpoint.api(
        parameter('flag', type=bool, required=True)
    )
    def api_test_bool(flag):
        return flag

    def age_validator(value):
        # test custom exception
        if value >= 150:
            raise Exception("you can't possibly be that old!")

        # test custom response
        if value >= 120:
            return Response('all lies', status=403)

        # test invalid response
        if value >= 110:
            return 1, 1

    @app.route('/api/test_validator')
    @endpoint.api(
        parameter('age', type=int, required=True, validator=age_validator)
    )
    def api_test_age_validator(age):
        return age

    @app.route('/api/test_broken_route')
    @endpoint.api(
        parameter('age', type=int, required=False, default=28)
    )
    def api_test_broken_route(age):
        raise Exception('whoops')

    @app.route('/api/test_status_code')
    @endpoint.api(
        parameter('age', type=int, required=False, default=28)
    )
    def api_test_status_code(age):
        return "203 test", 203

    @app.route('/api/test_bad_status_code')
    @endpoint.api(
        parameter('age', type=int, required=False, default=28)
    )
    def api_test_bad_status_code(age):
        return "203 test", 203, 1

    class UFO:
        def __init__(self):
            self.foo = 'bar'

    @app.route('/api/test_unknown_return')
    @endpoint.api(
        parameter('age', type=int, required=False, default=28)
    )
    def api_test_unknown_return(age):
        return UFO()

    @app.route('/api/test_empty_return')
    @endpoint.api()
    def api_test_empty_return():
        return

    @app.route('/api/test_custom_return')
    @endpoint.api()
    def api_test_custom_return():
        return Response("foo", 203)

    @app.route('/api/test_docstring')
    @endpoint.api(
        parameter("foo", default="bar", type=str)
    )
    def api_test_docstring(foo):
        """
        Just a test. With multiple
        lines.
        :param foo: bar!
        :param faulty line, should be ignored as a param.
        :return: Nothing, really.
        """
        raise Exception('whoops')

    @app.route('/api/test_types', methods=["GET", 'POST'])
    @endpoint.api(
        parameter('a', type=str, required=True),
        parameter('b', type=int, required=True),
        parameter('c', type=dict, required=False),
        parameter('d', type=list, required=False),
        parameter('e', type=datetime, required=True),
        parameter('f', type=bool, required=False)
    )
    def api_test_types(a, b, c, d, e, f):
        return [a, b, c, d, e, f]

    if sys.version_info >= (3, 5):
        @app.route('/api/test_type_annotations')
        @endpoint.api(
            parameter('name', required=True),
            parameter('age', required=False)
        )
        def api_test_type_annotations(name: str, age: int, location: str = "Amsterdam"):
            return {"name": name, "age": age, "location": location}

        @app.route('/api/test_type_annotations_fail')
        @endpoint.api(
            parameter('name', required=True),
            parameter('age', required=False)
        )
        def api_test_type_annotations_fail(name: str, age):
            return {"name": name, "age": age}

    return app


if __name__ == '__main__':
    app = create_app()