# Flask-YoloAPI

![whoop](https://i.imgur.com/xVS3UGq.png)

A simple framework for creating clean Flask API endpoints.

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

Whoa, that was easy! Let's look at the response:

```javascript
{
    status: true,
    data: "user logged in!"
}
```

Use cases
-------------

- You don't want to fish incoming parameters out of `request.args`, or wait, was it `request.form`? No, it is `request.json`. Ugh!
    - (Even if you do manage to extract them out of the `request` object, you then need to check their validity on type and value)
- You don't want to write boilerplate code that involves classes just to make some API routes (flask-restful).
- You don't need to hook your endpoints directly to SQLa models.
- You don't care about providing REST compliancy - you just want a JSON endpoint, damnit!

In short, this is a simple library for simple JSON endpoints.


## Error handling

When the view function itself raises an exception, a JSON response is generated that includes:

- The error message
- Docstring of the view function
- HTTP 500

This error response is also generated when endpoint requirements are not met.

```javascript
{
    status: false,
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

## Return values
In the example above, a string was returned. The following types are also supported:

- `str`, `unicode`, `int`, `float`, `dict`, `list`, `datetime`.

```python
@app.route('/wishlist')
@endpoint.api(
    parameter('category', type=str, required=False)
)
def shopping_list(category):
    return ['volvo xc60', 'mclaren mp4-12c']
```

```javascript
{
    "status": true
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
def view_function():
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
    "status": true,
    "data": {
        "age": 27, 
        "name": "sander"
    }
}
```

## Default values

You can define default values to endpoint parameters by giving them a `default` argument.

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
    "status": true,
    "data": {
        "age": 10, 
        "name": "sander"
    }
}
```

## Custom validators

Additional parameter validation can be done by providing the `validator` argument. 

This function takes 1 parameter; the input. An `Exception` must be raised when the validation proves to be unsuccessful.

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
    "data": "parameter 'age' error: you can't possibly be that old!", 
    "status": false
}
```

## Parameter handling

This library is rather opportunistic about gathering incoming parameters, as it will check in the following 3 places:

- `request.args`
- `request.json`
- `request.form`

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
app.json_encoder = CustomJSONEncoder
```

License
-------------
MIT.
