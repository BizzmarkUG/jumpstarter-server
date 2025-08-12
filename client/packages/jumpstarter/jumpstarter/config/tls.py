"""TLS configuration for jumpstarter."""

from pydantic import BaseModel, Field


class TLSConfigV1Alpha1(BaseModel):
    """TLS configuration for connections."""
    insecure: bool = Field(default=False)
    ca_file: str | None = Field(default=None)
    cert_file: str | None = Field(default=None) 
    key_file: str | None = Field(default=None)