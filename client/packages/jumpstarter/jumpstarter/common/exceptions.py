"""Common exceptions for jumpstarter."""


class JumpstarterError(Exception):
    """Base exception for jumpstarter errors."""
    pass


class ConfigurationError(JumpstarterError):
    """Configuration-related errors."""
    pass


class ConnectionError(JumpstarterError):
    """Connection-related errors."""
    def set_config(self, config):
        """Set the config that caused the error."""
        pass


class FileNotFoundError(JumpstarterError):
    """File not found errors."""
    pass