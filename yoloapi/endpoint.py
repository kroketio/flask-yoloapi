from functools import wraps
from datetime import datetime

from flask import jsonify

from yoloapi.utils import decorator_parametrized, docstring, get_request_data

SUPPORTED_TYPES = (int, float, str, list, dict, unicode, datetime, None)


@decorator_parametrized
def api(view_func, *parameters):
    """YOLO!"""
    messages = {
        "required": "argument '%s' is required",
        "type_error": "wrong type for argument '%s' "
                      "should be of type '%s'",
        "bad_return": "view function returned unsupported type '%s'",
        "bad_return_tuple": "when returning tuples, the first index "
                            "must be an object of any supported "
                            "return type, the second a valid "
                            "HTTP return status code as an integer"
    }

    func_err = lambda ex, http_status=500: (jsonify({
        'status': False,
        'data': str(ex),
        'docstring': docstring(view_func, *parameters)}
    ), http_status)

    @wraps(view_func)
    def validate_and_execute(*args, **kwargs):
        # grabs incoming data (multiple methods)
        request_data = get_request_data()

        for param in parameters:
            # checks if param is required
            if param.key not in request_data:
                if param.required:
                    return func_err(messages['required'] % param.key)
                else:
                    # set default value, if provided
                    if param.default is not None:
                        kwargs[param.key] = param.default
                    else:
                        kwargs[param.key] = None
                    continue

            # validate the param value
            value = request_data.get(param.key)
            if type(value) != param.type:
                if issubclass(param.type, (int, float)):
                    try:
                        value = param.type(value)  # opportunistic coercing to int/float
                    except ValueError:
                        return func_err(messages['type_error'] % (param.key, param.type))
                elif issubclass(param.type, (str, unicode)):
                    pass
                else:
                    return func_err(messages['type_error'] % (param.key, param.type))

            # validate via custom validator, if provided
            if 'validator' in param.kwargs:
                try:
                    param.kwargs['validator'](value)
                except Exception as ex:
                    return func_err("parameter '%s' error: %s" % (param.key, str(ex)))

            kwargs[param.key] = value
        try:
            result = view_func(*args, **kwargs)
        except Exception as ex:
            return func_err('view function returned an error: %s' % str(ex))

        if result is None:
            return jsonify({'status': True, 'data': None}), 204

        # if view function returned a tuple, do http status code
        elif isinstance(result, tuple):
            if not len(result) == 2 or not isinstance(result[1], int):
                return func_err(messages['bad_return_tuple'])
            return jsonify({'status': True, 'data': result[0]}), result[1]

        elif not isinstance(result, SUPPORTED_TYPES):
            raise Exception('Bad return type for api_result')

        return jsonify({'status': True, 'data': result})
    return validate_and_execute


class parameter:
    def __init__(self, key, type, default=None, required=False, validator=None):
        if not isinstance(key, (str, unicode)):
            raise Exception("bad type for 'key'; must be 'str'")
        if not isinstance(required, bool):
            raise Exception("bad type for 'required'; must be 'bool'")
        if not issubclass(type, SUPPORTED_TYPES):
            raise Exception("parameter type '%s' not supported" % str(type))
        if default is not None and default.__class__ not in SUPPORTED_TYPES:
            raise Exception("parameter default of type '%s' not supported" % str(type(default)))
        if validator is not None and not callable(validator):
            raise Exception("parameter 'validator' must be a function")

        self.kwargs = {"validator": validator}
        self.default = default
        self.key = str(key)
        self.type = type
        self.required = required
