"""Common configuration structures."""

from os import getenv
from pathlib import Path

from pydantic import BaseModel

# For standalone server, we'll use a simpler config path
CONFIG_API_VERSION = "jumpstarter.dev/v1alpha1"
CONFIG_PATH = Path(getenv("JMP_CLIENT_CONFIG_HOME", Path.home() / ".config" / "jumpstarter"))


class ObjectMeta(BaseModel):
    """Kubernetes-style object metadata."""
    namespace: str | None = None
    name: str