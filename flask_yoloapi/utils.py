from flask import request

from flask_yoloapi.exceptions import UnknownParameterType


def docstring(view_func, *parameters):
    """Takes a view function, generates an object out of
    the docstring"""
    _docstring = view_func.__doc__
    if not _docstring:
        return

    data = {
        "params": {},
        "return": None,
        "help": ""
    }

    for line in _docstring.strip().split("\n"):
        line = line.strip()

        if line.startswith(":param "):
            line = line[7:]
            if ":" not in line:
                continue

            k, v = line.split(':', 1)
            v = v.strip()

            try:
                param = next(param for param in parameters if param.key == k)
                required = param.required if param.required else False

                if param.type is None:
                    raise UnknownParameterType()

                param = {
                    "type": param.type.__name__,
                    "required": required
                }
            except StopIteration:
                param = {
                    "type": None,
                    "required": False,
                    "error": "docstring doesnt include this param"
                }
            except UnknownParameterType:
                param = {
                    "type": None,
                    "required": required,
                    "error": "could not determine type"
                }

            param["help"] = v
            data["params"][k] = param
            continue

        elif line.startswith(":return: "):
            data["return"] = line[9:]
            continue

        data["help"] += "%s " % line

    data["help"] = data["help"].strip()
    return data


def get_request_data():
    """Very complicated and extensive algorithm
    to fetch incoming request data regardless
    of the type of request"""
    locations = ['args', 'form', 'json']
    data = {k: {} for k in locations}
    data['all'] = {}

    for location in locations:
        _data = getattr(request, location)
        if _data:
            for k, v in _data.items():
                data[location][k] = v
                data['all'][k] = v
        else:
            data[location] = {}
    return data


def decorator_parametrized(dec):
    """So we can give multiple arguments to a decorator"""
    def layer(*args, **kwargs):
        def repl(view_func):
            return dec(view_func, *args, **kwargs)
        return repl
    return layer
