"""gRPC client for jumpstarter standalone server."""

import grpc
from typing import Optional, Dict, Any, List
import logging
from .config.client import ClientConfigV1Alpha1
from .config.user import UserConfigV1Alpha1
from .config.grpc import call_credentials

logger = logging.getLogger(__name__)


class JumpstarterClient:
    """Client for connecting to jumpstarter standalone server."""
    
    def __init__(self, endpoint: str = None, token: str = None):
        """Initialize client with endpoint and optional token."""
        if endpoint is None or token is None:
            # Try to load from current client config
            try:
                user_config = UserConfigV1Alpha1.load()
                current_client = user_config.config.current_client
                if current_client:
                    client_config = ClientConfigV1Alpha1.load(current_client)
                    endpoint = endpoint or client_config.endpoint
                    token = token or client_config.token
            except Exception:
                pass
        
        if endpoint is None:
            endpoint = "localhost:8080"
            
        self.endpoint = endpoint
        self.token = token
        self._channel = None
        
    def _get_channel(self):
        """Get or create gRPC channel."""
        if self._channel is None:
            # For standalone mode, use insecure channel
            self._channel = grpc.insecure_channel(self.endpoint)
            
        return self._channel
        
    def _get_credentials(self):
        """Get call credentials if token is available."""
        if self.token:
            return call_credentials("client", {}, self.token)
        return None
        
    def close(self):
        """Close the gRPC channel."""
        if self._channel:
            self._channel.close()
            self._channel = None
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def test_connection(self) -> bool:
        """Test if we can connect to the server."""
        try:
            with self._get_channel() as channel:
                # Try to connect with a simple health check
                try:
                    future = grpc.channel_ready_future(channel)
                    future.result(timeout=5.0)
                    return True
                except grpc.FutureTimeoutError:
                    return False
        except Exception as e:
            logger.debug(f"Connection test failed: {e}")
            return False
    
    def list_leases(self) -> List[str]:
        """List leases for the current client."""
        # For now, return a mock response
        # TODO: Implement actual gRPC call to controller service
        logger.info("Listing leases (mock response)")
        return ["lease-001", "lease-002"]
    
    def request_lease(self, selector: Dict[str, str], duration: str = "30m") -> str:
        """Request a new lease."""
        # For now, return a mock response
        # TODO: Implement actual gRPC call to controller service  
        logger.info(f"Requesting lease with selector {selector}, duration {duration}")
        return "lease-new-123"
        
    def release_lease(self, lease_name: str) -> bool:
        """Release a lease."""
        # For now, return a mock response
        # TODO: Implement actual gRPC call to controller service
        logger.info(f"Releasing lease {lease_name}")
        return True
        
    def get_devices(self, selector: str = None) -> List[Dict[str, Any]]:
        """Get devices/exporters from the server."""
        # For now, return a mock response showing the structure works
        # TODO: Implement actual gRPC call to controller service
        logger.info(f"Getting devices with selector: {selector}")
        return [
            {
                "name": "mock-device-1",
                "namespace": "default", 
                "labels": {"type": "device", "model": "pi4"},
                "status": "available"
            },
            {
                "name": "mock-device-2", 
                "namespace": "default",
                "labels": {"type": "device", "model": "jetson"},
                "status": "leased"
            }
        ]