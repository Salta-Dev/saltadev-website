"""Tests for saltadev/logging.py module."""

import pytest
from saltadev.logging import configure_logging, get_logger


class TestConfigureLogging:
    """Tests for configure_logging function."""

    def test_configures_without_error(self):
        """Should configure logging without raising errors."""
        # Reset the configured flag for testing
        import saltadev.logging

        saltadev.logging._configured = False
        configure_logging()
        assert saltadev.logging._configured is True

    def test_only_configures_once(self):
        """Should only configure logging once."""
        import saltadev.logging

        saltadev.logging._configured = False
        configure_logging()
        configure_logging()  # Second call should be a no-op
        assert saltadev.logging._configured is True


class TestGetLogger:
    """Tests for get_logger function."""

    def test_returns_logger_instance(self):
        """Should return a logger instance."""
        logger = get_logger()
        assert logger is not None

    def test_logger_has_info_method(self):
        """Logger should have info method."""
        logger = get_logger()
        assert hasattr(logger, "info")
        assert callable(logger.info)

    def test_logger_has_warning_method(self):
        """Logger should have warning method."""
        logger = get_logger()
        assert hasattr(logger, "warning")
        assert callable(logger.warning)

    def test_logger_has_error_method(self):
        """Logger should have error method."""
        logger = get_logger()
        assert hasattr(logger, "error")
        assert callable(logger.error)

    def test_returns_same_logger(self):
        """Should return the same logger instance."""
        logger1 = get_logger()
        logger2 = get_logger()
        assert logger1 is logger2
