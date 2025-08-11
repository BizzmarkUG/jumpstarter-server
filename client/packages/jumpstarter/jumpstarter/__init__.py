"""Jumpstarter core library."""

__version__ = "1.0.0"

# Basic client stub - full implementation will come from the original jumpstarter repository
class JumpstarterClient:
    """Basic Jumpstarter client for connecting to the standalone server."""
    
    def __init__(self, server_url: str = "localhost:8080"):
        """Initialize client with server URL."""
        self.server_url = server_url
    
    def connect(self):
        """Connect to the jumpstarter server."""
        print(f"Connecting to {self.server_url}...")
        print("Full client implementation coming soon.")
    
    def list_devices(self):
        """List available devices."""
        print("Device listing functionality coming soon.")
        return []


__all__ = ["JumpstarterClient"]