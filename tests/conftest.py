# conftest.py
import pytest

from tests.mock_app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.debug = True
    return app
