"""
Testes adicionais para casos extremos e caminhos específicos de código
que não estão sendo cobertos pelos testes existentes.
"""

import io
import json
import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from logging_metrics.core import (
    ColoredFormatter,
    JSONFormatter,
    create_console_handler,
    create_file_handler,
    create_timed_file_handler,
    get_logger,
    log_spark_dataframe_info,
    setup_file_logging,
)


class TestColoredFormatterEdgeCases:
    """Testes para casos extremos do ColoredFormatter."""

    def test_format_preserves_original_attributes(self):
        """Test that format() preserves original record attributes."""
        formatter = ColoredFormatter(use_colors=True)
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Original message",
            args=(),
            exc_info=None,
        )

        original_levelname = record.levelname
        original_msg = record.msg

        # Format the record
        formatted = formatter.format(record)

        # Check that original attributes are restored
        assert record.levelname == original_levelname
        assert record.msg == original_msg
        assert formatted is not None

    def test_format_with_exception_during_formatting(self):
        """Test ColoredFormatter behavior when super().format() raises exception."""
        formatter = ColoredFormatter(use_colors=True)
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        original_levelname = record.levelname
        original_msg = record.msg

        # Mock super().format() to raise an exception
        with patch.object(logging.Formatter, "format", side_effect=Exception("Format error")):
            with pytest.raises(Exception, match="Format error"):
                formatter.format(record)

            # Even after exception, original attributes should be restored
            assert record.levelname == original_levelname
            assert record.msg == original_msg


class TestJSONFormatterEdgeCases:
    """Testes para casos extremos do JSONFormatter."""

    def test_format_with_circular_reference(self):
        """Test JSONFormatter with circular reference in extra data."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Create circular reference
        circular_obj = {}
        circular_obj["self"] = circular_obj
        record.circular = circular_obj

        # Should handle circular reference gracefully
        formatted = formatter.format(record)
        data = json.loads(formatted)

        # Should convert to string representation
        assert "circular" in data
        assert isinstance(data["circular"], str)


class TestFileHandlerEdgeCases:
    """Testes para casos extremos dos file handlers."""

    def test_create_file_handler_with_pathlib_path(self):
        """Test create_file_handler with pathlib.Path object."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "test.log"

            handler = create_file_handler(
                log_file=log_path,  # Using Path object instead of string
                max_bytes=1024,
                backup_count=2,
            )

            assert handler is not None
            assert isinstance(handler, logging.handlers.RotatingFileHandler)
            handler.close()

    def test_create_timed_file_handler_with_all_when_options(self):
        """Test create_timed_file_handler with all valid 'when' options."""
        valid_when_options = [
            "S",
            "M",
            "H",
            "D",
            "W0",
            "W1",
            "W2",
            "W3",
            "W4",
            "W5",
            "W6",
            "midnight",
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            for when_option in valid_when_options:
                log_path = Path(tmp_dir) / f"test_{when_option}.log"

                handler = create_timed_file_handler(
                    log_file=log_path, when=when_option, interval=1, backup_count=1
                )

                assert handler is not None
                handler.close()


class TestConsoleHandlerEdgeCases:
    """Testes para casos extremos do console handler."""

    def test_create_console_handler_with_custom_stream(self):
        """Test create_console_handler with custom stream."""
        custom_stream = io.StringIO()

        handler = create_console_handler(
            level=logging.DEBUG, use_colors=False, stream=custom_stream
        )

        assert handler is not None
        assert handler.stream == custom_stream
        handler.close()

    def test_create_console_handler_with_custom_formatter(self):
        """Test create_console_handler with custom formatter."""
        custom_formatter = logging.Formatter("Custom: %(message)s")

        handler = create_console_handler(level=logging.INFO, formatter=custom_formatter)

        assert handler is not None
        assert handler.formatter == custom_formatter
        handler.close()


class TestGetLoggerEdgeCases:
    """Testes para casos extremos do get_logger."""

    def test_get_logger_with_mixed_handler_types(self):
        """Test get_logger with different types of handlers."""
        stream_handler = logging.StreamHandler()

        with tempfile.TemporaryDirectory() as tmp_dir:
            file_handler = create_file_handler(log_file=Path(tmp_dir) / "test.log")

            logger = get_logger(
                "mixed_handlers",
                level=logging.DEBUG,
                handlers=[stream_handler, file_handler],
                propagate=False,
            )

            assert len(logger.handlers) == 2
            assert stream_handler in logger.handlers
            assert file_handler in logger.handlers

            # Cleanup
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)

    def test_get_logger_caplog_friendly_removes_existing_handlers(self):
        """Test that caplog_friendly mode removes existing handlers."""
        logger = get_logger("test_caplog_removal")

        # Add multiple handlers
        handler1 = logging.StreamHandler()
        handler2 = logging.StreamHandler()
        logger.addHandler(handler1)
        logger.addHandler(handler2)

        assert len(logger.handlers) == 2

        # Configure as caplog_friendly
        logger = get_logger("test_caplog_removal", caplog_friendly=True)

        assert len(logger.handlers) == 0
        assert logger.propagate is True


class TestSetupFileLoggingEdgeCases:
    """Testes para casos extremos do setup_file_logging."""

    def test_setup_file_logging_with_special_characters_in_prefix(self):
        """Test setup_file_logging with various special characters in file_prefix."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            special_chars_prefix = "test@#$%^&*()+=[]{}|;:,.<>?"

            logger = setup_file_logging(
                "test_special", log_dir=tmp_dir, file_prefix=special_chars_prefix
            )

            assert logger is not None

            # Check that file was created with sanitized name
            files = list(Path(tmp_dir).glob("**/*.log"))
            assert len(files) > 0

            logger.close()

    def test_setup_file_logging_with_all_special_chars_prefix(self):
        """Test setup_file_logging where file_prefix becomes empty after sanitization."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Only special characters that will be completely stripped
            all_special_prefix = "@#$%^&*()+=[]{|}:;<>?"

            logger = setup_file_logging(
                "test_empty_prefix",
                log_dir=tmp_dir,
                file_prefix=all_special_prefix,
                add_console=False,
            )

            assert logger is not None

            # Should use "application" as fallback
            files = list(Path(tmp_dir).glob("**/*application*"))
            assert len(files) > 0

            logger.close()

    def test_setup_file_logging_size_rotation_path(self):
        """Test the size rotation code path that's not commonly tested."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            logger = setup_file_logging(
                "size_test",
                log_dir=tmp_dir,
                rotation="size",  # This triggers the else branch
                max_bytes=512,
                backup_count=2,
                add_console=False,
            )

            assert logger is not None

            # Log enough to potentially trigger rotation
            for i in range(50):
                logger.info(f"Log message {i} with enough content to fill up space")

            logger.close()

    def test_setup_file_logging_json_format_console_path(self):
        """Test JSON format with console handler path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            logger = setup_file_logging(
                "json_console_test",
                log_dir=tmp_dir,
                json_format=True,
                add_console=True,
                use_colors=False,  # JSON format ignores colors anyway
            )

            assert logger is not None

            # Test that both handlers use JSON format
            file_handler = None
            console_handler = None

            for handler in logger.handlers:
                if isinstance(handler, logging.handlers.TimedRotatingFileHandler):
                    file_handler = handler
                elif isinstance(handler, logging.StreamHandler):
                    console_handler = handler

            assert file_handler is not None
            assert console_handler is not None
            assert isinstance(file_handler.formatter, JSONFormatter)
            assert isinstance(console_handler.formatter, JSONFormatter)

            logger.close()


class TestSparkDataFrameLoggingEdgeCases:
    """Testes para casos extremos do log_spark_dataframe_info."""

    def test_log_spark_dataframe_info_sample_error_handling(self):
        """Test sample data display error handling."""
        logger = logging.getLogger("sample_error_test")

        # Mock DataFrame with limit/toPandas that raises exception
        mock_df = Mock()
        mock_df.count.return_value = 100
        mock_df.limit.return_value.toPandas.side_effect = Exception("Sample error")

        with patch.object(logger, "error") as mock_error:
            log_spark_dataframe_info(mock_df, logger, show_sample=True)
            mock_error.assert_called()


class TestIntegrationScenarios:
    """Testes de integração para cenários complexos."""

    def test_full_logging_pipeline_with_errors(self, caplog):
        """Test complete logging pipeline with various error conditions."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Setup complex logger configuration
            logger = setup_file_logging(
                "integration.test.complex",
                log_dir=tmp_dir,
                log_folder="complex_test/",
                file_prefix="integration",
                level=logging.DEBUG,
                console_level=logging.WARNING,
                rotation="time",
                backup_count=3,
                add_console=True,
                use_colors=True,
                json_format=False,
                utc="Europe/London",
            )

            # Test hierarchical logging
            child_logger = logging.getLogger("integration.test.complex.child")
            child_logger.setLevel(logging.INFO)

            # Generate various log levels
            logger.debug("Debug message - should only go to file")
            logger.info("Info message - file and console")
            logger.warning("Warning message - file and console")
            logger.error("Error message - file and console")
            logger.critical("Critical message - file and console")

            child_logger.info("Child logger message")

            # Test with exception
            try:
                raise ValueError("Integration test exception")
            except ValueError:
                logger.error("Exception occurred", exc_info=True)

            # Test with extra data
            logger.info("User action", extra={"user_id": 12345, "action": "login"})

            # Verify files were created
            log_files = list(Path(tmp_dir).rglob("*.log"))
            assert len(log_files) > 0

            # Verify log content
            for log_file in log_files:
                content = log_file.read_text()
                assert "Info message" in content
                assert "Warning message" in content
                assert "Error message" in content
                assert "Critical message" in content
                assert "Integration test exception" in content

            logger.close()

    def test_logger_cleanup_and_recreation(self):
        """Test logger cleanup and recreation scenarios."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create logger
            logger1 = setup_file_logging("cleanup_test", log_dir=tmp_dir)
            logger1.info("First logger message")

            # Close logger
            logger1.close()

            # Create new logger with same name
            logger2 = setup_file_logging("cleanup_test", log_dir=tmp_dir)
            logger2.info("Second logger message")

            # Both should work without interference
            assert logger1.name == logger2.name

            logger2.close()

    def test_concurrent_logging_simulation(self):
        """Test concurrent logging simulation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            logger = setup_file_logging(
                "concurrent_test",
                log_dir=tmp_dir,
                max_bytes=1024,  # Small size to trigger rotation
                backup_count=5,
            )

            # Simulate concurrent logging
            for i in range(100):
                logger.info(f"Concurrent message {i}: " + "x" * 50)
                if i % 10 == 0:
                    logger.warning(f"Warning at iteration {i}")
                if i % 25 == 0:
                    logger.error(f"Error at iteration {i}")

            # Check that files were created and rotated
            log_files = list(Path(tmp_dir).rglob("*"))
            assert len(log_files) > 0

            logger.close()


# Test para testar o fechamento de handlers com exceção
def test_handler_cleanup_with_exceptions():
    """Test handler cleanup when close() methods raise exceptions."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        logger = setup_file_logging("cleanup_exception_test", log_dir=tmp_dir)

        # Create mock handlers that raise exceptions
        mock_handler1 = Mock()
        mock_handler1.flush.side_effect = Exception("Flush error")
        mock_handler1.close.side_effect = Exception("Close error")

        mock_handler2 = Mock()
        mock_handler2.flush.return_value = None
        mock_handler2.close.side_effect = Exception("Close error 2")

        # Add mock handlers to logger
        logger.handlers.extend([mock_handler1, mock_handler2])

        # Should handle exceptions gracefully and print warnings
        with patch("builtins.print") as mock_print:
            logger.close()

            # Should have printed warnings for exceptions
            assert mock_print.call_count >= 2

            # Check that removeHandler was called for all handlers
            assert mock_handler1 not in logger.handlers
            assert mock_handler2 not in logger.handlers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
