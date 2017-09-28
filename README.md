# Flask-YoloAPI

![whoop](https://i.imgur.com/xVS3UGq.png)

A small framework for creating simple JSON endpoints.

Example
-------

```python
from flask_yoloapi import endpoint, parameter

@app.route('/api/login', methods=['GET', 'POST'])
@endpoint.api(
    parameter('username', type=str, required=True),
    parameter('password', type=str, required=True),
    parameter('remember', type=bool, required=False, default=False)
)
def login(username, password, remember):
    """
    Logs the user in.
    :param username: The username of the user
    :param password: The password of the user
    :param expiration: Session expiration time in seconds
    :return: The logged in message!
    """
    return "user logged in!"
```

The response:

```javascript
{
    data: "user logged in!"
}
```

Use cases
-------------

- You don't want to write boilerplate code that involves classes just to make some API routes (flask-restful).
- You don't want to fish incoming parameters out of `request.args`, or wait, was it `request.form`? No, `request.json` :sleeping:
- You don't need to hook your endpoints directly to SQLa models.
- You don't care about providing REST compliancy - you just want somewhat consistent JSON endpoints, damnit!

In short, this is a simple library for simple JSON endpoints.


Installation
------------
```sh
pip install flask-yoloapi
```


## Return values
In the example above, a string was returned. The following types are also supported:

- `str`, `unicode`, `int`, `float`, `dict`, `list`, `datetime`, `bool`, `flask.Response`.

```python
@app.route('/wishlist')
@endpoint.api(
    parameter('category', type=str, required=False)
)
def wishlist(category):
    if category == "cars":
        return ['volvo xc60', 'mclaren mp4-12c']
```

```javascript
{
    "data": [
        "volvo xc60", 
        "mclaren mp4-12c"
    ]
}
``` 

## HTTP status codes

To return different status codes, return a 2-length `tuple` with the second index being the status code itself.

```python
@app.route('/create_foo')
@endpoint.api()
def create_foo():
    return 'created', 201
```

## Route parameters

You can still use Flask's route parameters in conjunction with endpoint parameters.

```python
@app.route('/hello/<name>')
@endpoint.api(
    parameter('age', type=int, required=True)
)
def hello(name, age):
    return {'name': name, 'age': age}
```

`/hello/sander?age=27`

```javascript
{
    "data": {
        "age": 27, 
        "name": "sander"
    }
}
```

## Default values

You can define default values for endpoint parameters via `default`.

```python
@app.route('/hello/<name>')
@endpoint.api(
    parameter('age', type=int, required=False, default=10)
)
def hello(name, age):
    return {'name': name, 'age': age}
```
`/hello/sander`
```javascript
{
    "data": {
        "age": 10, 
        "name": "sander"
    }
}
```

## Type annotations

Parameter types are required, except when type annotations are in use.

A Python 3.5 example:

```python
@app.route('/hello/', methods=['POST'])
@endpoint.api(
    parameter('age', required=True),
    parameter('name', required=True)
)
def hello(name: str, age: int):
    return {'name': name, 'age': age}
```

Python 2 equivalent:

```python
@app.route('/hello/', methods=['POST'])
@endpoint.api(
    parameter('age', type=int, required=True),
    parameter('name', type=str, required=True)
)
def hello(name, age):
    return {'name': name, 'age': age}
```

Note that type annotations are only supported from Python 3.5 and upwards (PEP 484).

## Custom validators

Additional parameter validation can be done by providing a validator function. This function takes 1 parameter; the input. 

An `Exception` must be raised when the validation proves to be unsuccessful.

```python
def custom_validator(value):
    if value > 120:
        raise Exception("you can't possibly be that old!")

@app.route('/hello/<name>')
@endpoint.api(
    parameter('age', type=int, required=True, validator=custom_validator)
)
def hello(name, age):
    return {'name': name, 'age': age}
```

`/hello/sander?age=130`

```javascript
{
    "data": "parameter 'age' error: you can't possibly be that old!"
}
```

If you need more flexibility regarding incoming types use the `flask_yoloapi.types.ANY` type.

## Parameter handling

This library is rather opportunistic about gathering incoming parameters, as it will check in the following 3 places:

- `request.args`
- `request.json`
- `request.form`

An optional `location` argument can be provided to specify the source of the parameter.

```python
@app.route('/login')
@endpoint.api(
    parameter('username', type=str, location='form', required=True),
    parameter('password', type=str, location='form', required=True),
)
def login(username, password):
    return "Wrong password!", 403
```

The following 3 locations are supported:

- `args` - GET parameters
- `form` - parameters submitted via HTTP form submission
- `json` - parameters submitted via a JSON encoded HTTP request

## Datetime format

To output datetime objects in `ISO 8601` format (which are trivial to parse in Javascript via `Date.parse()`), use a custom JSON encoder.

```python
from datetime import date
from flask.json import JSONEncoder

class ApiJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super(ApiJsonEncoder, self).default(obj)

app = Flask(__name__)
app.json_encoder = ApiJsonEncoder
```


## Error handling

When the view function itself raises an exception, a JSON response is generated that includes:

- The error message
- Docstring of the view function
- HTTP 500

This error response is also generated when endpoint requirements are not met.

```javascript
{
    data: "argument 'password' is required",
    docstring: {
        help: "Logs the user in.",
        return: "The logged in message!",
        params: {
            username: {
                help: "The username of the user",
                required: true,
                type: "str"
                }
            },
        ...
```


License
-------------
MIT.
