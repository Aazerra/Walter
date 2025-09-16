"""
Walter - A modern Project Manager and Project generator.

This module contains the main Walter class and CLI entry point.
"""

import argparse
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Protocol

from charondb import LiteManager, MySQLManager
from tabulate import tabulate

from .lib.db_wrapper import SimpleLiteWrapper
from .lib.project_creators import ProjectCreatorFactory
from .lib.types import Config, Database, Project

BASE_DIR = os.environ["HOME"]
PACKAGE_DIR = Path(__file__).parent
CONFIG_TEMPLATE = PACKAGE_DIR / "config.json"
USER_CONFIG = Path(BASE_DIR) / ".config" / "walter.json"

if not USER_CONFIG.exists():
    USER_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_TEMPLATE.exists():
        shutil.copyfile(str(CONFIG_TEMPLATE), str(USER_CONFIG))


class DatabaseProtocol(Protocol):
    """Protocol for database implementations."""

    def select(
        self, table: str, columns: list[str], where: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """Select data from the database."""
        ...

    def insert(self, table: str, columns: list[str], values: list[Any]) -> None:
        """Insert data into the database."""
        ...

    def exists(self, table: str, where: str) -> bool:
        """Check if a record exists."""
        ...


class Walter:
    """Main Walter application class."""

    def __init__(self) -> None:
        """Initialize the Walter application."""
        self.parser = self._create_parser()
        self.args = self.parser.parse_args()

        # Initialize configuration
        self.config = Config(str(USER_CONFIG))
        self.project_base_dir = Path(BASE_DIR) / self.config.project_dir

        # Initialize components
        self.storage = self._init_database()
        self.logger = self._init_logger(self.args.debug)

        # Ensure directories exist
        if not self.config.init:
            self._setup_directories()
            self.config.init = True
            self.config.write()

    def _init_database(self) -> DatabaseProtocol:
        """Initialize database connection."""
        db: Database = self.config.database
        if db.driver == "mysql":
            return MySQLManager(
                username=db.username,
                password=db.password,
                host=db.host,
                database=db.name,
                port=db.port,
                debug=self.args.debug,
            )
        else:
            # Use SQLite wrapper
            wrapper = SimpleLiteWrapper(db.name or "walter.db")
            if not self.config.init:
                wrapper.init_database()
            return wrapper

    def _init_logger(self, debug: bool) -> logging.Logger:
        """Initialize logger."""
        logger = logging.getLogger("Walter")
        logger.handlers.clear()  # Clear any existing handlers

        formatter = logging.Formatter("%(asctime)s -> %(message)s")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        return logger

    def _setup_directories(self) -> None:
        """Set up required directories."""
        paths = ["project_dir", "complete_dir", "incomplete_dir"]
        for path_name in paths:
            path = Path(BASE_DIR) / getattr(self.config, path_name)
            path.mkdir(parents=True, exist_ok=True)

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            description="Walter - A Project Manager and Project generator"
        )
        parser.add_argument(
            "-p", "--project", help="Name of project you want to work with"
        )
        parser.add_argument(
            "-d", "--debug", help="Enable verbose logging", action="store_true"
        )

        subparsers = parser.add_subparsers(
            help="command to run on your project", dest="command", required=True
        )

        # Mark command
        mark_parser = subparsers.add_parser(
            "mark", description="Mark project as complete or incomplete"
        )
        mark_parser.add_argument(
            "mark", help="Project status", choices=["incom", "com"], metavar="STATUS"
        )

        # Create command
        create_parser = subparsers.add_parser(
            "create", description="Create a new project"
        )
        create_parser.add_argument(
            "-l",
            "--language",
            help="Programming language for the project",
            required=True,
            choices=ProjectCreatorFactory.get_supported_languages(),
            metavar="LANGUAGE",
        )

        # List command
        subparsers.add_parser("list", description="List all projects")

        return parser

    def check_arg(self, args: argparse.Namespace) -> None:
        """Execute the command specified in args."""
        command_method = getattr(self, args.command)
        command_method()

    def list(self) -> None:
        """List all projects in a formatted table."""
        projects = self.storage.select("project_tbl", ["*"])
        columns = ["id", "name", "language", "completed"]
        projects_list = []

        for project in projects:
            projects_list.append(list(Project(project)))

        print(tabulate(projects_list, columns, "fancy_grid"))

    def create_symlink(self, path: Path, name: str) -> None:
        """Create a symbolic link for the project."""
        self.logger.info("Creating symlink")
        target_dir = Path(BASE_DIR) / self.config.incomplete_dir / name

        if target_dir.exists():
            self.logger.warning("Symlink already exists")
        else:
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            target_dir.symlink_to(path)

    def create(self) -> None:
        """Create a new project."""
        if not self.args.project:
            self.logger.error(
                "Project name is required. Use -p/--project to specify it."
            )
            return

        language = self.args.language
        name = self.args.project
        path = self.project_base_dir / name

        # Check if project already exists in database
        if self.storage.exists("project_tbl", f'name="{name}"'):
            self.logger.error("Project already exists in database!")
            return

        # Get the appropriate project creator
        creator = ProjectCreatorFactory.get_creator(language, self.logger)
        if not creator:
            self.logger.error(f"Unsupported language: {language}")
            return

        # Create the project
        if creator.create_project(path, name):
            self.create_symlink(path, name)
            self.storage.insert(
                "project_tbl", ["name", "language", "complete"], [name, language, 0]
            )
            self.logger.info("Project created successfully")
        else:
            self.logger.error("Failed to create project")

    def mark(self) -> None:
        """Mark a project as complete or incomplete."""
        if not self.args.project:
            self.logger.error(
                "Project name is required. Use -p/--project to specify it."
            )
            return

        name = self.args.project
        user_mark = self.args.mark

        def toggle(mark: str, project_name: str) -> None:
            """Toggle project status between complete and incomplete."""
            now = "com" if mark == "incom" else "incom"
            current_dir = (
                Path(BASE_DIR) / getattr(self.config, mark + "plete_dir") / project_name
            )
            target_dir = (
                Path(BASE_DIR) / getattr(self.config, now + "plete_dir") / project_name
            )
            project_path = self.project_base_dir / project_name

            status_text = "Completed" if mark == "com" else "Incomplete"

            if current_dir.exists():
                self.logger.warning(f"Project already marked as: {status_text}")
                return

            if target_dir.exists():
                # Remove old symlink and create new one
                target_dir.unlink()

            current_dir.parent.mkdir(parents=True, exist_ok=True)
            current_dir.symlink_to(project_path)
            self.logger.info(f"Project marked as: {status_text}")

        toggle(user_mark, name)


def main() -> None:
    """Main entry point for the Walter CLI."""
    try:
        walter = Walter()
        walter.check_arg(walter.args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
