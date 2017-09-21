from flask import request


def docstring(view_func, *parameters):
    """Takes a view function, generates an object out of the docstring"""
    _docstring = view_func.func_doc
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
            k, v = line[7:].split(': ', 1)

            try:
                param = next({"type": param.type.__name__,
                              "required": param.required}
                             for param in parameters if param.key == k)
            except StopIteration:
                param = {"type": None, "required": None}

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
    data = {}
    if request.args:
        data = request.args

    if request.json:
        for k, v in request.json.items():
            data[k] = v
    elif request.form:
        for k, v in request.form.items():
            data[k] = v
    return data


def decorator_parametrized(dec):
    """So we can give multiple arguments to a decorator"""
    def layer(*args, **kwargs):
        def repl(view_func):
            return dec(view_func, *args, **kwargs)
        return repl
    return layer
