"""
Type definitions for Walter configuration and data models.

This module contains the core data classes and configuration handling.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator


@dataclass
class Database:
    """Database configuration."""

    driver: str
    username: str
    password: str
    name: str
    port: int
    host: str

    def __init__(self, config_obj: Dict[str, Any]) -> None:
        """Initialize from configuration dictionary."""
        self.driver = config_obj["driver"]
        self.username = config_obj["username"]
        self.password = config_obj["password"]
        self.name = config_obj["name"]
        self.port = config_obj["port"]
        self.host = config_obj["host"]


class Config:
    """Configuration manager for Walter."""

    def __init__(self, config_file: str) -> None:
        """Initialize configuration from file."""
        self.config_file = Path(config_file)

        with open(self.config_file, "r", encoding="utf-8") as json_file:
            config = json.load(json_file)

        self.database = Database(config["database"])
        self.project_dir: str = config["project_dir"]
        self.complete_dir: str = config["complete_dir"]
        self.incomplete_dir: str = config["incomplete_dir"]
        self.init: bool = config["init"]

    def write(self) -> None:
        """Write configuration back to file."""
        config_dict = {
            "init": self.init,
            "project_dir": self.project_dir,
            "complete_dir": self.complete_dir,
            "incomplete_dir": self.incomplete_dir,
            "database": {
                "driver": self.database.driver,
                "name": self.database.name,
                "username": self.database.username,
                "password": self.database.password,
                "host": self.database.host,
                "port": self.database.port,
            },
        }

        with open(self.config_file, "w", encoding="utf-8") as json_file:
            json.dump(config_dict, json_file, indent=4, sort_keys=True)


@dataclass
class Project:
    """Project data model."""

    id: int
    name: str
    language: str
    complete: bool

    def __init__(self, obj: Dict[str, Any]) -> None:
        """Initialize from database row dictionary."""
        self.id = obj["id"]
        self.name = obj["name"]
        self.language = obj["language"]
        self.complete = bool(obj["complete"])

    def __iter__(self) -> Iterator[Any]:
        """Allow iteration over project fields for tabulation."""
        yield self.id
        yield self.name
        yield self.language
        yield self.complete
