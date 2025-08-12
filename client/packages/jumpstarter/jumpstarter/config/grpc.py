"""GRPC configuration utilities."""

def call_credentials(user_type: str, metadata, token: str):
    """Create call credentials for gRPC - simplified for standalone mode."""
    # For standalone mode, we'll implement basic token-based auth
    import grpc
    
    def add_auth_header(context, callback):
        callback((("authorization", f"Bearer {token}"),), None)
    
    return grpc.metadata_call_credentials(add_auth_header)