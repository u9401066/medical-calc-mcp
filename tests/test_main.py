"""
Tests for src/main.py

Tests for main entry point functions and CLI argument parsing.
"""

from unittest.mock import MagicMock, patch


class TestCreateServer:
    """Tests for create_server function"""

    def test_create_server_returns_server(self) -> None:
        """Test that create_server returns a MedicalCalculatorServer instance"""
        from src.infrastructure.mcp.server import MedicalCalculatorServer
        from src.main import create_server

        server = create_server()
        assert isinstance(server, MedicalCalculatorServer)

    def test_create_server_has_registry(self) -> None:
        """Test that the created server has a populated registry"""
        from src.main import create_server

        server = create_server()
        assert server.registry is not None
        # Should have at least 68 calculators
        assert len(server.registry.list_all()) >= 68

    def test_create_server_with_custom_host_port(self) -> None:
        """Test create_server with custom host and port"""
        from src.main import create_server

        server = create_server(host="127.0.0.1", port=9999)
        assert server is not None
        # Verify the config was applied
        assert server._config.host == "127.0.0.1"
        assert server._config.port == 9999


class TestArgumentParsing:
    """Tests for main() argument parsing"""

    def test_default_mode_is_stdio(self) -> None:
        """Test that default mode is stdio"""
        from src.main import main

        with patch('sys.argv', ['main.py']):
            with patch('src.main.create_server') as mock_create:
                mock_server = MagicMock()
                mock_create.return_value = mock_server
                with patch('src.main.logger'):
                    main()
                    mock_server.run.assert_called_once_with(transport="stdio")

    def test_sse_mode(self) -> None:
        """Test SSE mode"""
        from src.main import main

        with patch('sys.argv', ['main.py', '--mode', 'sse']):
            with patch('src.main.create_server') as mock_create:
                mock_server = MagicMock()
                mock_create.return_value = mock_server
                with patch('src.main.logger'):
                    main()
                    mock_create.assert_called_once_with(host='0.0.0.0', port=8000)
                    mock_server.run.assert_called_once_with(transport="sse")

    def test_sse_mode_with_custom_port(self) -> None:
        """Test SSE mode with custom port"""
        from src.main import main

        with patch('sys.argv', ['main.py', '--mode', 'sse', '--port', '9000']):
            with patch('src.main.create_server') as mock_create:
                mock_server = MagicMock()
                mock_create.return_value = mock_server
                with patch('src.main.logger'):
                    main()
                    mock_create.assert_called_once_with(host='0.0.0.0', port=9000)

    def test_http_mode(self) -> None:
        """Test HTTP mode is called correctly"""
        from src.main import main

        with patch('sys.argv', ['main.py', '--mode', 'http']):
            with patch('src.main.create_server') as mock_create:
                mock_server = MagicMock()
                mock_create.return_value = mock_server
                with patch('src.main.logger'):
                    main()
                    mock_server.run.assert_called_once_with(transport="http")

    def test_custom_host(self) -> None:
        """Test custom host parameter"""
        from src.main import main

        with patch('sys.argv', ['main.py', '--mode', 'sse', '--host', '127.0.0.1', '--port', '3000']):
            with patch('src.main.create_server') as mock_create:
                mock_server = MagicMock()
                mock_create.return_value = mock_server
                with patch('src.main.logger'):
                    main()
                    mock_create.assert_called_once_with(host='127.0.0.1', port=3000)

    def test_env_mode_override(self) -> None:
        """Test environment variable mode override"""
        import os

        from src.main import main

        with patch.dict(os.environ, {'MCP_MODE': 'sse', 'MCP_PORT': '7000'}):
            with patch('sys.argv', ['main.py']):
                with patch('src.main.create_server') as mock_create:
                    mock_server = MagicMock()
                    mock_create.return_value = mock_server
                    with patch('src.main.logger'):
                        main()
                        mock_create.assert_called_once_with(host='0.0.0.0', port=7000)
                        mock_server.run.assert_called_once_with(transport="sse")


class TestLogging:
    """Tests for logging configuration"""

    def test_logger_exists(self) -> None:
        """Test logger is properly configured"""
        from src.main import logger
        assert logger is not None

    def test_logging_configured_with_env(self) -> None:
        """Test logging level from environment"""
        import os

        with patch.dict(os.environ, {'LOG_LEVEL': 'DEBUG'}):
            # Re-import to apply env var
            import importlib

            import src.main
            importlib.reload(src.main)

            # Verify logger exists
            assert src.main.logger is not None


class TestModulePath:
    """Tests for module path configuration"""

    def test_imports_work(self) -> None:
        """Test that imports work correctly"""
        from src.main import create_server, main
        assert create_server is not None
        assert main is not None

