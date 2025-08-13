"""Shell configuration."""

from pydantic import BaseModel


class ShellConfigV1Alpha1(BaseModel):
    """Shell configuration - simplified for standalone mode."""
    pass