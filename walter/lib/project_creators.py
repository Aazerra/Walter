"""
Project Creator implementations using the Strategy pattern.

This module provides different project creation strategies for various languages.
"""

import logging
import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, Type


class ProjectCreator(ABC):
    """Abstract base class for project creators."""

    def __init__(self, logger: logging.Logger):
        """Initialize the project creator with a logger."""
        self.logger = logger

    @abstractmethod
    def create_project(self, path: Path, name: str) -> bool:
        """Create a project at the given path with the given name.

        Args:
            path: The path where the project should be created
            name: The name of the project

        Returns:
            True if the project was created successfully, False otherwise
        """
        pass

    def _ensure_directory(self, path: Path) -> None:
        """Ensure the project directory exists."""
        if path.exists():
            self.logger.warning(f"Project directory {path} already exists")
        else:
            self.logger.info(f"Creating project directory: {path}")
            path.mkdir(parents=True, exist_ok=True)


class PythonProjectCreator(ProjectCreator):
    """Creates Python projects with virtual environments."""

    def create_project(self, path: Path, name: str) -> bool:
        """Create a Python project with a virtual environment."""
        try:
            self._ensure_directory(path)

            venv_path = path / "venv"
            self.logger.info("Creating project virtualenv")

            # Use subprocess to create virtualenv
            subprocess.run(["python", "-m", "virtualenv", str(venv_path)], check=True)

            # Create a basic requirements.txt
            requirements_file = path / "requirements.txt"
            with open(requirements_file, "w") as f:
                f.write("# Add your project dependencies here\n")

            # Create a basic main.py
            main_file = path / "main.py"
            with open(main_file, "w") as f:
                f.write(f'"""Main module for {name}."""\n\n')
                f.write("def main():\n")
                f.write(f'    print("Hello from {name}!")\n\n')
                f.write('if __name__ == "__main__":\n')
                f.write("    main()\n")

            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create Python project: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error creating Python project: {e}")
            return False


class NodeProjectCreator(ProjectCreator):
    """Creates Node.js projects."""

    def create_project(self, path: Path, name: str) -> bool:
        """Create a Node.js project with yarn init."""
        try:
            self._ensure_directory(path)

            self.logger.info("Running yarn init")
            subprocess.run(["yarn", "init", "-y"], cwd=str(path), check=True)

            # Create a basic index.js
            index_file = path / "index.js"
            with open(index_file, "w") as f:
                f.write(f"// Main file for {name}\n\n")
                f.write(f'console.log("Hello from {name}!");\n')

            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create Node.js project: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error creating Node.js project: {e}")
            return False


class GoProjectCreator(ProjectCreator):
    """Creates Go projects."""

    def create_project(self, path: Path, name: str) -> bool:
        """Create a Go project with go mod init."""
        try:
            self._ensure_directory(path)

            self.logger.info("Initializing Go module")
            subprocess.run(["go", "mod", "init", name], cwd=str(path), check=True)

            # Create a basic main.go
            main_file = path / "main.go"
            with open(main_file, "w") as f:
                f.write("package main\n\n")
                f.write('import "fmt"\n\n')
                f.write("func main() {\n")
                f.write(f'\tfmt.Println("Hello from {name}!")\n')
                f.write("}\n")

            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create Go project: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error creating Go project: {e}")
            return False


class PHPProjectCreator(ProjectCreator):
    """Creates PHP projects."""

    def create_project(self, path: Path, name: str) -> bool:
        """Create a PHP project with composer init."""
        try:
            self._ensure_directory(path)

            # Create a basic index.php
            index_file = path / "index.php"
            with open(index_file, "w") as f:
                f.write("<?php\n\n")
                f.write(f"// Main file for {name}\n\n")
                f.write(f'echo "Hello from {name}!";\n')

            # Try to initialize composer if available
            try:
                self.logger.info("Initializing composer")
                subprocess.run(
                    ["composer", "init", "--no-interaction"], cwd=str(path), check=True
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.logger.warning("Composer not available, skipping composer init")

            return True
        except Exception as e:
            self.logger.error(f"Unexpected error creating PHP project: {e}")
            return False


class LuaProjectCreator(ProjectCreator):
    """Creates Lua projects."""

    def create_project(self, path: Path, name: str) -> bool:
        """Create a Lua project."""
        try:
            self._ensure_directory(path)

            # Create a basic main.lua
            main_file = path / "main.lua"
            with open(main_file, "w") as f:
                f.write(f"-- Main file for {name}\n\n")
                f.write(f'print("Hello from {name}!")\n')

            return True
        except Exception as e:
            self.logger.error(f"Unexpected error creating Lua project: {e}")
            return False


class ProjectCreatorFactory:
    """Factory for creating project creators."""

    _creators: Dict[str, Type[ProjectCreator]] = {
        "python": PythonProjectCreator,
        "node": NodeProjectCreator,
        "go": GoProjectCreator,
        "php": PHPProjectCreator,
        "lua": LuaProjectCreator,
    }

    @classmethod
    def get_creator(
        cls, language: str, logger: logging.Logger
    ) -> Optional[ProjectCreator]:
        """Get a project creator for the specified language.

        Args:
            language: The programming language
            logger: Logger instance

        Returns:
            A ProjectCreator instance or None if language is not supported
        """
        creator_class = cls._creators.get(language.lower())
        if creator_class:
            return creator_class(logger)
        return None

    @classmethod
    def get_supported_languages(cls) -> list[str]:
        """Get list of supported languages."""
        return list(cls._creators.keys())
