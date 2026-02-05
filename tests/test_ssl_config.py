"""
Tests for SSL/TLS Configuration

Tests for the SslConfig class and SSL integration with MCP server.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.infrastructure.mcp.config import SslConfig


class TestSslConfigDataclass:
    """Tests for SslConfig dataclass creation"""

    def test_default_values(self) -> None:
        """Test default SslConfig values"""
        config = SslConfig()
        assert config.enabled is False
        assert config.keyfile is None
        assert config.certfile is None
        assert config.ca_certs is None
        assert config.cert_required is False

    def test_custom_values(self) -> None:
        """Test SslConfig with custom values"""
        config = SslConfig(
            enabled=True,
            keyfile="/path/to/key.pem",
            certfile="/path/to/cert.pem",
            ca_certs="/path/to/ca.pem",
            cert_required=True
        )
        assert config.enabled is True
        assert config.keyfile == "/path/to/key.pem"
        assert config.certfile == "/path/to/cert.pem"
        assert config.ca_certs == "/path/to/ca.pem"
        assert config.cert_required is True


class TestSslConfigFromEnv:
    """Tests for SslConfig.from_env() method"""

    def test_from_env_default(self) -> None:
        """Test from_env with no environment variables"""
        with patch.dict(os.environ, {}, clear=True):
            config = SslConfig.from_env()
            assert config.enabled is False
            assert config.keyfile is None
            assert config.certfile is None

    def test_from_env_ssl_enabled_true(self) -> None:
        """Test SSL_ENABLED=true"""
        env = {
            "SSL_ENABLED": "true",
            "SSL_KEYFILE": "/path/to/key.pem",
            "SSL_CERTFILE": "/path/to/cert.pem"
        }
        with patch.dict(os.environ, env, clear=True):
            config = SslConfig.from_env()
            assert config.enabled is True
            assert config.keyfile == "/path/to/key.pem"
            assert config.certfile == "/path/to/cert.pem"

    def test_from_env_ssl_enabled_1(self) -> None:
        """Test SSL_ENABLED=1"""
        env = {"SSL_ENABLED": "1"}
        with patch.dict(os.environ, env, clear=True):
            config = SslConfig.from_env()
            assert config.enabled is True

    def test_from_env_ssl_enabled_yes(self) -> None:
        """Test SSL_ENABLED=yes"""
        env = {"SSL_ENABLED": "yes"}
        with patch.dict(os.environ, env, clear=True):
            config = SslConfig.from_env()
            assert config.enabled is True

    def test_from_env_ssl_enabled_on(self) -> None:
        """Test SSL_ENABLED=on"""
        env = {"SSL_ENABLED": "on"}
        with patch.dict(os.environ, env, clear=True):
            config = SslConfig.from_env()
            assert config.enabled is True

    def test_from_env_ssl_enabled_false(self) -> None:
        """Test SSL_ENABLED=false"""
        env = {"SSL_ENABLED": "false"}
        with patch.dict(os.environ, env, clear=True):
            config = SslConfig.from_env()
            assert config.enabled is False

    def test_from_env_ssl_enabled_invalid(self) -> None:
        """Test SSL_ENABLED with invalid value defaults to false"""
        env = {"SSL_ENABLED": "invalid"}
        with patch.dict(os.environ, env, clear=True):
            config = SslConfig.from_env()
            assert config.enabled is False

    def test_from_env_with_ca_certs(self) -> None:
        """Test SSL_CA_CERTS environment variable"""
        env = {
            "SSL_ENABLED": "true",
            "SSL_KEYFILE": "/path/to/key.pem",
            "SSL_CERTFILE": "/path/to/cert.pem",
            "SSL_CA_CERTS": "/path/to/ca.pem"
        }
        with patch.dict(os.environ, env, clear=True):
            config = SslConfig.from_env()
            assert config.ca_certs == "/path/to/ca.pem"

    def test_from_env_cert_required(self) -> None:
        """Test SSL_CERT_REQUIRED=true"""
        env = {
            "SSL_ENABLED": "true",
            "SSL_KEYFILE": "/path/to/key.pem",
            "SSL_CERTFILE": "/path/to/cert.pem",
            "SSL_CERT_REQUIRED": "true"
        }
        with patch.dict(os.environ, env, clear=True):
            config = SslConfig.from_env()
            assert config.cert_required is True

    def test_from_env_case_insensitive(self) -> None:
        """Test environment variable values are case-insensitive"""
        env = {
            "SSL_ENABLED": "TRUE",
            "SSL_CERT_REQUIRED": "YES"
        }
        with patch.dict(os.environ, env, clear=True):
            config = SslConfig.from_env()
            assert config.enabled is True
            assert config.cert_required is True


class TestSslConfigValidation:
    """Tests for SslConfig.validate() method"""

    def test_validate_disabled_ssl(self) -> None:
        """Test validation passes when SSL is disabled"""
        config = SslConfig(enabled=False)
        # Should not raise
        config.validate()

    def test_validate_missing_keyfile(self) -> None:
        """Test validation fails when SSL enabled but keyfile missing"""
        config = SslConfig(enabled=True, certfile="/path/to/cert.pem")
        with pytest.raises(ValueError, match="SSL_KEYFILE is required"):
            config.validate()

    def test_validate_missing_certfile(self) -> None:
        """Test validation fails when SSL enabled but certfile missing"""
        config = SslConfig(enabled=True, keyfile="/path/to/key.pem")
        with pytest.raises(ValueError, match="SSL_CERTFILE is required"):
            config.validate()

    def test_validate_keyfile_not_found(self) -> None:
        """Test validation fails when keyfile doesn't exist"""
        config = SslConfig(
            enabled=True,
            keyfile="/nonexistent/key.pem",
            certfile="/nonexistent/cert.pem"
        )
        with pytest.raises(ValueError, match="SSL keyfile not found"):
            config.validate()

    def test_validate_certfile_not_found(self) -> None:
        """Test validation fails when certfile doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "key.pem"
            key_path.write_text("dummy key")

            config = SslConfig(
                enabled=True,
                keyfile=str(key_path),
                certfile="/nonexistent/cert.pem"
            )
            with pytest.raises(ValueError, match="SSL certfile not found"):
                config.validate()

    def test_validate_ca_certs_not_found(self) -> None:
        """Test validation fails when ca_certs specified but doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "key.pem"
            cert_path = Path(tmpdir) / "cert.pem"

            key_path.write_text("dummy key")
            cert_path.write_text("dummy cert")

            config = SslConfig(
                enabled=True,
                keyfile=str(key_path),
                certfile=str(cert_path),
                ca_certs="/nonexistent/ca.pem"
            )
            with pytest.raises(ValueError, match="SSL CA certs file not found"):
                config.validate()

    def test_validate_all_files_exist(self) -> None:
        """Test validation passes when all files exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "key.pem"
            cert_path = Path(tmpdir) / "cert.pem"
            ca_path = Path(tmpdir) / "ca.pem"

            # Create dummy files
            key_path.write_text("dummy key")
            cert_path.write_text("dummy cert")
            ca_path.write_text("dummy ca")

            config = SslConfig(
                enabled=True,
                keyfile=str(key_path),
                certfile=str(cert_path),
                ca_certs=str(ca_path)
            )
            # Should not raise
            config.validate()

    def test_validate_without_ca_certs(self) -> None:
        """Test validation passes without optional ca_certs"""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "key.pem"
            cert_path = Path(tmpdir) / "cert.pem"

            key_path.write_text("dummy key")
            cert_path.write_text("dummy cert")

            config = SslConfig(
                enabled=True,
                keyfile=str(key_path),
                certfile=str(cert_path)
            )
            # Should not raise
            config.validate()


class TestSslConfigIntegration:
    """Integration tests for SSL configuration with server"""

    def test_create_server_with_ssl_params(self) -> None:
        """Test create_server accepts SSL parameters"""
        from src.main import create_server

        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "key.pem"
            cert_path = Path(tmpdir) / "cert.pem"

            key_path.write_text("dummy key")
            cert_path.write_text("dummy cert")

            server = create_server(
                ssl_keyfile=str(key_path),
                ssl_certfile=str(cert_path)
            )

            assert server is not None
            # Verify SSL config was applied
            assert server._config.ssl.keyfile == str(key_path)
            assert server._config.ssl.certfile == str(cert_path)

    def test_create_server_without_ssl(self) -> None:
        """Test create_server works without SSL"""
        from src.main import create_server

        server = create_server()
        assert server is not None
        assert server._config.ssl.enabled is False

    def test_mcp_server_config_includes_ssl(self) -> None:
        """Test McpServerConfig includes SSL configuration"""
        from src.infrastructure.mcp.config import McpServerConfig, SslConfig

        ssl_config = SslConfig(enabled=True, keyfile="/key.pem", certfile="/cert.pem")
        config = McpServerConfig(ssl=ssl_config)

        assert config.ssl.enabled is True
        assert config.ssl.keyfile == "/key.pem"

    def test_main_with_ssl_cli_args(self) -> None:
        """Test main() accepts SSL CLI arguments"""
        from unittest.mock import MagicMock

        from src.main import main

        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "key.pem"
            cert_path = Path(tmpdir) / "cert.pem"

            key_path.write_text("dummy key")
            cert_path.write_text("dummy cert")

            with patch('sys.argv', [
                'main.py',
                '--mode', 'sse',
                '--ssl-keyfile', str(key_path),
                '--ssl-certfile', str(cert_path)
            ]):
                with patch('src.main.create_server') as mock_create:
                    mock_server = MagicMock()
                    mock_create.return_value = mock_server
                    with patch('src.main.logger'):
                        main()
                        # Verify SSL params were passed
                        mock_create.assert_called_once()
                        call_kwargs = mock_create.call_args[1]
                        assert call_kwargs['ssl_keyfile'] == str(key_path)
                        assert call_kwargs['ssl_certfile'] == str(cert_path)

    def test_main_with_ssl_env_vars(self) -> None:
        """Test main() reads SSL config from environment"""
        from unittest.mock import MagicMock

        from src.main import main

        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "key.pem"
            cert_path = Path(tmpdir) / "cert.pem"

            key_path.write_text("dummy key")
            cert_path.write_text("dummy cert")

            env = {
                'MCP_MODE': 'sse',
                'SSL_KEYFILE': str(key_path),
                'SSL_CERTFILE': str(cert_path)
            }

            with patch.dict(os.environ, env, clear=False):
                with patch('sys.argv', ['main.py']):
                    with patch('src.main.create_server') as mock_create:
                        mock_server = MagicMock()
                        mock_create.return_value = mock_server
                        with patch('src.main.logger'):
                            main()
                            # Verify server was created (env vars read by config)
                            mock_create.assert_called_once()


class TestSslConfigEdgeCases:
    """Edge case tests for SSL configuration"""

    def test_empty_string_paths(self) -> None:
        """Test behavior with empty string paths"""
        config = SslConfig(
            enabled=True,
            keyfile="",
            certfile=""
        )
        with pytest.raises(ValueError, match="SSL_KEYFILE is required"):
            config.validate()

    def test_whitespace_paths(self) -> None:
        """Test paths with only whitespace"""
        config = SslConfig(
            enabled=False,
            keyfile="   ",
            certfile="   "
        )
        # Should pass because SSL is disabled
        config.validate()

    def test_relative_paths(self) -> None:
        """Test relative file paths work"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory and create relative paths
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)

                key_path = Path("ssl/key.pem")
                cert_path = Path("ssl/cert.pem")
                key_path.parent.mkdir(parents=True, exist_ok=True)

                key_path.write_text("dummy key")
                cert_path.write_text("dummy cert")

                config = SslConfig(
                    enabled=True,
                    keyfile="ssl/key.pem",
                    certfile="ssl/cert.pem"
                )
                # Should not raise
                config.validate()
            finally:
                os.chdir(original_cwd)

    def test_unicode_paths(self) -> None:
        """Test Unicode characters in file paths"""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_path = Path(tmpdir) / "密鑰.pem"
            cert_path = Path(tmpdir) / "證書.pem"

            key_path.write_text("dummy key")
            cert_path.write_text("dummy cert")

            config = SslConfig(
                enabled=True,
                keyfile=str(key_path),
                certfile=str(cert_path)
            )
            # Should not raise
            config.validate()
