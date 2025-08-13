"""User configuration management."""

from pathlib import Path
from typing import ClassVar, Literal

import yaml
from pydantic import BaseModel, Field

from .common import CONFIG_PATH
from ..common.exceptions import FileNotFoundError


class UserConfigContentV1Alpha1(BaseModel):
    """User configuration content."""
    current_client: str | None = Field(default=None)


class UserConfigV1Alpha1(BaseModel):
    """User configuration for jumpstarter CLI."""
    alias: str = Field(default="default")
    apiVersion: Literal["jumpstarter.dev/v1alpha1"] = Field(default="jumpstarter.dev/v1alpha1")
    kind: Literal["UserConfig"] = Field(default="UserConfig")
    
    config: UserConfigContentV1Alpha1 = Field(default_factory=UserConfigContentV1Alpha1)
    
    USER_CONFIG_PATH: ClassVar[Path] = CONFIG_PATH / "config.yaml"
    
    @classmethod
    def exists(cls) -> bool:
        """Check if user config exists."""
        return cls.USER_CONFIG_PATH.exists()
    
    @classmethod
    def load(cls):
        """Load user configuration."""
        if not cls.USER_CONFIG_PATH.exists():
            raise FileNotFoundError(f"User config '{cls.USER_CONFIG_PATH}' does not exist.")
        
        with open(cls.USER_CONFIG_PATH) as f:
            return cls.model_validate(yaml.safe_load(f))
    
    @classmethod
    def load_or_create(cls):
        """Load user config or create default if not exists."""
        if cls.exists():
            return cls.load()
        else:
            config = cls()
            cls.save(config)
            return config
    
    @classmethod
    def save(cls, config):
        """Save user configuration."""
        config.USER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config.USER_CONFIG_PATH, "w") as f:
            yaml.safe_dump(config.model_dump(mode="json", exclude={"alias"}), f, sort_keys=False)
        
        return config.USER_CONFIG_PATH
    
    def use_client(self, alias: str | None):
        """Set the current client configuration."""
        self.config.current_client = alias
        return self.save(self)