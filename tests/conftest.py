"""Pytest configuration and shared fixtures."""

pytest_plugins = [
    "tests.fixtures.recaptcha",
    "tests.fixtures.users",
    "tests.fixtures.cache",
    "tests.fixtures.http",
    "tests.fixtures.content",
    "tests.fixtures.locations",
    "tests.fixtures.benefits",
    "tests.fixtures.notifications",
    "tests.fixtures.password_reset",
]
