"""Client configuration for jumpstarter standalone mode."""

from __future__ import annotations

import os
from pathlib import Path
from typing import ClassVar, Literal, Optional, Self

import yaml
from pydantic import BaseModel, Field

from .common import CONFIG_PATH, ObjectMeta
from ..common.exceptions import FileNotFoundError
from .shell import ShellConfigV1Alpha1
from .tls import TLSConfigV1Alpha1


class ClientConfigV1Alpha1Drivers(BaseModel):
    """Driver configuration for client."""
    allow: list[str] = Field(default_factory=list)
    unsafe: bool = Field(default=False)


class ClientConfigV1Alpha1(BaseModel):
    """Client configuration for standalone mode."""
    CLIENT_CONFIGS_PATH: ClassVar[Path] = CONFIG_PATH / "clients"

    alias: str = Field(default="default")
    path: Path | None = Field(default=None)

    apiVersion: Literal["jumpstarter.dev/v1alpha1"] = Field(default="jumpstarter.dev/v1alpha1")
    kind: Literal["ClientConfig"] = Field(default="ClientConfig")

    metadata: ObjectMeta = Field(default_factory=ObjectMeta)

    endpoint: str | None = Field(default=None)
    tls: TLSConfigV1Alpha1 = Field(default_factory=TLSConfigV1Alpha1)
    token: str | None = Field(default=None)
    grpcOptions: dict[str, str | int] | None = Field(default_factory=dict)

    drivers: ClientConfigV1Alpha1Drivers = Field(default_factory=ClientConfigV1Alpha1Drivers)
    shell: ShellConfigV1Alpha1 = Field(default_factory=ShellConfigV1Alpha1)

    @classmethod
    def from_file(cls, path: os.PathLike):
        with open(path) as f:
            v = cls.model_validate(yaml.safe_load(f))
            v.alias = os.path.basename(path).split(".")[0]
            v.path = Path(path)
            return v

    @classmethod
    def ensure_exists(cls):
        """Check if the clients config dir exists, otherwise create it."""
        os.makedirs(cls.CLIENT_CONFIGS_PATH, exist_ok=True)

    @classmethod
    def _get_path(cls, alias: str) -> Path:
        """Get the regular path of a client config given an alias."""
        return (cls.CLIENT_CONFIGS_PATH / alias).with_suffix(".yaml")

    @classmethod
    def load(cls, alias: str) -> Self:
        """Load a client config by alias."""
        path = cls._get_path(alias)
        if path.exists() is False:
            raise FileNotFoundError(f"Client config '{path}' does not exist.")
        return cls.from_file(path)

    @classmethod
    def save(cls, config: Self, path: Optional[os.PathLike] = None) -> Path:
        """Saves a client config as YAML."""
        # Ensure the clients dir exists
        if path is None:
            cls.ensure_exists()
            # Set the config path before saving
            config.path = cls._get_path(config.alias)
        else:
            config.path = Path(path)
        with config.path.open(mode="w") as f:
            yaml.safe_dump(config.model_dump(mode="json", exclude={"path", "alias"}), f, sort_keys=False)
        return config.path

    @classmethod
    def dump_yaml(cls, config: Self) -> str:
        return yaml.safe_dump(config.model_dump(mode="json", exclude={"path", "alias"}), sort_keys=False)

    @classmethod
    def exists(cls, alias: str) -> bool:
        """Check if a client config exists by alias."""
        return cls._get_path(alias).exists()

    @classmethod
    def list(cls) -> ClientConfigListV1Alpha1:
        """List the available client configs."""
        from .user import UserConfigV1Alpha1

        if cls.CLIENT_CONFIGS_PATH.exists() is False:
            # Return an empty list if the dir does not exist
            return ClientConfigListV1Alpha1(
                currentConfig=None,  # Use the alias field name
                items=[],
            )

        results = os.listdir(cls.CLIENT_CONFIGS_PATH)
        # Only accept YAML files in the list
        files = filter(lambda x: x.endswith(".yaml"), results)

        def make_config(file: str):
            path = cls.CLIENT_CONFIGS_PATH / file
            return cls.from_file(path)

        current_config = None
        try:
            if UserConfigV1Alpha1.exists():
                user_config = UserConfigV1Alpha1.load()
                current_client = user_config.config.current_client
                current_config = current_client if current_client is not None else None
        except Exception as e:
            # If there's an issue loading user config, continue without current selection
            print(f"Warning: Could not load user config: {e}")
            current_config = None

        return ClientConfigListV1Alpha1(
            currentConfig=current_config,  # Use the alias field name
            items=list(map(make_config, files)),
        )

    @classmethod
    def delete(cls, alias: str) -> Path:
        """Delete a client config by alias."""
        path = cls._get_path(alias)
        if path.exists() is False:
            raise FileNotFoundError(f"Client config '{path}' does not exist.")
        path.unlink()
        return path


class ClientConfigListV1Alpha1(BaseModel):
    api_version: Literal["jumpstarter.dev/v1alpha1"] = Field(alias="apiVersion", default="jumpstarter.dev/v1alpha1")
    current_config: Optional[str] = Field(alias="currentConfig", default=None)
    items: list[ClientConfigV1Alpha1]
    kind: Literal["ClientConfigList"] = Field(default="ClientConfigList")

    def dump_json(self):
        return self.model_dump_json(indent=4, by_alias=True)

    def dump_yaml(self):
        return yaml.safe_dump(self.model_dump(mode="json", by_alias=True), indent=2)

    @classmethod
    def rich_add_columns(cls, table):
        table.add_column("CURRENT")
        table.add_column("ALIAS")
        table.add_column("ENDPOINT")
        table.add_column("PATH")

    def rich_add_rows(self, table):
        for client in self.items:
            table.add_row(
                "*" if self.current_config == client.alias else "",
                client.alias,
                client.endpoint,
                str(client.path),
            )