import pytest
from unittest.mock import patch
import time
from lambda_function import lambda_handler, request_counts


# Reiniciar los contadores de requests antes de cada test
@pytest.fixture(autouse=True)
def reset_request_counts():
    request_counts.clear()


def create_event(path):
    return {"path": path, "httpMethod": "GET", "headers": {}, "requestContext": {"identity": {"sourceIp": "127.0.0.1"}}}


def test_root_path():
    event = create_event("/")
    response = lambda_handler(event, None)
    assert response['statusCode'] == 200
    assert "API Proxy is running" in response['body']


@patch.dict('lambda_function.limits', {r"^/categories/.*$": 3})
def test_categories_rate_limit_exceeded_mocked():
    event = create_event("/categories/MLA1055")
    limit = 3

    for _ in range(limit):
        response = lambda_handler(event, None)
        assert response['statusCode'] == 200

    response = lambda_handler(event, None)
    assert response['statusCode'] == 429
    assert "Too Many Requests" in response['body']


@patch.dict('lambda_function.limits', {r"^/categories/.*$": 3})
def test_categories_rate_limit_reset_after_minute_mocked():
    event = create_event("/categories/MLA1055")
    limit = 3

    for _ in range(limit):
        lambda_handler(event, None)

    time.sleep(61)
    response = lambda_handler(event, None)
    assert response['statusCode'] == 200


@patch.dict('lambda_function.limits', {r"^/sites/MLA/categories$": 5})
def test_sites_categories_rate_limit_exceeded_mocked():
    event = create_event("/sites/MLA/categories")
    limit = 5

    for _ in range(limit):
        response = lambda_handler(event, None)
        assert response['statusCode'] == 200

    response = lambda_handler(event, None)
    assert response['statusCode'] == 429
    assert "Too Many Requests" in response['body']


@patch.dict('lambda_function.limits', {r"^/items/.*$": 2})
def test_items_rate_limit_exceeded_mocked():
    event = create_event("/items/MLA811601010")
    limit = 2

    for _ in range(limit):
        response = lambda_handler(event, None)
        assert response['statusCode'] == 401

    response = lambda_handler(event, None)
    assert response['statusCode'] == 429
    assert "Too Many Requests" in response['body']
