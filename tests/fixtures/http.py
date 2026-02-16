"""HTTP request/response fixtures for testing."""

import pytest
from django.test import RequestFactory


@pytest.fixture
def request_factory():
    """Return a Django RequestFactory instance."""
    return RequestFactory()


@pytest.fixture
def get_request(request_factory):
    """Return a factory for creating GET requests."""

    def _make_request(path="/", **kwargs):
        request = request_factory.get(path, **kwargs)
        request.META["REMOTE_ADDR"] = "127.0.0.1"
        return request

    return _make_request


@pytest.fixture
def post_request(request_factory):
    """Return a factory for creating POST requests."""

    def _make_request(path="/", data=None, **kwargs):
        request = request_factory.post(path, data=data or {}, **kwargs)
        request.META["REMOTE_ADDR"] = "127.0.0.1"
        return request

    return _make_request


@pytest.fixture
def request_with_ip(request_factory):
    """Return a factory for creating requests with custom IP."""

    def _make_request(ip, method="GET", path="/", data=None):
        if method == "POST":
            request = request_factory.post(path, data=data or {})
        else:
            request = request_factory.get(path)
        request.META["REMOTE_ADDR"] = ip
        return request

    return _make_request


@pytest.fixture
def request_with_forwarded_ip(request_factory):
    """Return a factory for creating requests with X-Forwarded-For header."""

    def _make_request(forwarded_ip, method="GET", path="/"):
        if method == "POST":
            request = request_factory.post(path)
        else:
            request = request_factory.get(path)
        request.META["HTTP_X_FORWARDED_FOR"] = forwarded_ip
        request.META["REMOTE_ADDR"] = "10.0.0.1"
        return request

    return _make_request


@pytest.fixture
def request_with_fingerprint(request_factory):
    """Return a factory for creating requests with fingerprint cookie."""

    def _make_request(fingerprint, method="GET", path="/"):
        if method == "POST":
            request = request_factory.post(path)
        else:
            request = request_factory.get(path)
        request.META["REMOTE_ADDR"] = "127.0.0.1"
        request.COOKIES["sd_fp"] = fingerprint
        return request

    return _make_request
