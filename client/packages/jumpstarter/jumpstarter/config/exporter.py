"""Exporter configuration for jumpstarter standalone mode."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar, Literal, Optional, Self

import yaml
from pydantic import BaseModel, Field

from .common import CONFIG_PATH, ObjectMeta
from .tls import TLSConfigV1Alpha1


class ExporterConfigV1Alpha1(BaseModel):
    """Exporter configuration for standalone mode."""
    
    # Use local config path instead of /etc for standalone mode
    BASE_PATH: ClassVar[Path] = CONFIG_PATH / "exporters"

    alias: str = Field(default="default")

    apiVersion: Literal["jumpstarter.dev/v1alpha1"] = Field(default="jumpstarter.dev/v1alpha1")
    kind: Literal["ExporterConfig"] = Field(default="ExporterConfig")
    metadata: ObjectMeta

    endpoint: str | None = Field(default=None)
    tls: TLSConfigV1Alpha1 = Field(default_factory=TLSConfigV1Alpha1)
    token: str | None = Field(default=None)
    grpcOptions: dict[str, str | int] | None = Field(default_factory=dict)

    # Simplified export configuration for standalone mode
    export: dict[str, Any] = Field(default_factory=dict)

    path: Path | None = Field(default=None)

    @classmethod
    def _get_path(cls, alias: str):
        return (cls.BASE_PATH / alias).with_suffix(".yaml")

    @classmethod
    def exists(cls, alias: str):
        return cls._get_path(alias).exists()

    @classmethod
    def load_path(cls, path: Path):
        with path.open() as f:
            config = cls.model_validate(yaml.safe_load(f))
            config.path = path
            return config

    @classmethod
    def load(cls, alias: str) -> Self:
        config = cls.load_path(cls._get_path(alias))
        config.alias = alias
        return config

    @classmethod
    def list(cls) -> ExporterConfigListV1Alpha1:
        exporters = []
        if cls.BASE_PATH.exists():
            for entry in cls.BASE_PATH.iterdir():
                if entry.suffix == ".yaml":
                    exporters.append(cls.load(entry.stem))
        return ExporterConfigListV1Alpha1(items=exporters)

    @classmethod
    def dump_yaml(cls, config: Self) -> str:
        return yaml.safe_dump(config.model_dump(mode="json", exclude={"alias", "path"}), sort_keys=False)

    @classmethod
    def save(cls, config: Self, path: Optional[str] = None) -> Path:
        # Set the config path before saving
        if path is None:
            config.path = cls._get_path(config.alias)
            config.path.parent.mkdir(parents=True, exist_ok=True)
        else:
            config.path = Path(path)
        with config.path.open(mode="w") as f:
            yaml.safe_dump(config.model_dump(mode="json", exclude={"alias", "path"}), f, sort_keys=False)
        return config.path

    @classmethod
    def delete(cls, alias: str) -> Path:
        path = cls._get_path(alias)
        path.unlink(missing_ok=True)
        return path


class ExporterConfigListV1Alpha1(BaseModel):
    api_version: Literal["jumpstarter.dev/v1alpha1"] = Field(alias="apiVersion", default="jumpstarter.dev/v1alpha1")
    items: list[ExporterConfigV1Alpha1]
    kind: Literal["ExporterConfigList"] = Field(default="ExporterConfigList")

    @classmethod
    def rich_add_columns(cls, table):
        table.add_column("ALIAS")
        table.add_column("ENDPOINT") 
        table.add_column("PATH")

    def rich_add_rows(self, table):
        for exporter in self.items:
            table.add_row(
                exporter.alias,
                exporter.endpoint or "N/A",
                str(exporter.path),
            )