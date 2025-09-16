"""Basic tests for Walter functionality."""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from walter.lib.db_wrapper import SimpleLiteWrapper
from walter.lib.project_creators import ProjectCreatorFactory, PythonProjectCreator


def test_python_project_creator():
    """Test Python project creation."""
    logger = Mock()
    creator = PythonProjectCreator(logger)

    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test_project"

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value = None
            result = creator.create_project(project_path, "test_project")

            assert result is True
            assert project_path.exists()
            assert (project_path / "requirements.txt").exists()
            assert (project_path / "main.py").exists()

            # Check content of main.py
            main_content = (project_path / "main.py").read_text()
            assert "test_project" in main_content
            assert "def main():" in main_content


def test_project_creator_factory():
    """Test the project creator factory."""
    logger = Mock()

    # Test valid language
    creator = ProjectCreatorFactory.get_creator("python", logger)
    assert isinstance(creator, PythonProjectCreator)

    # Test invalid language
    creator = ProjectCreatorFactory.get_creator("invalid", logger)
    assert creator is None

    # Test supported languages
    languages = ProjectCreatorFactory.get_supported_languages()
    assert "python" in languages
    assert "node" in languages
    assert "go" in languages


def test_simple_lite_wrapper():
    """Test the SQLite database wrapper."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name

    try:
        wrapper = SimpleLiteWrapper(db_path)
        wrapper.init_database()

        # Test table creation
        cursor = wrapper.connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='project_tbl'"
        )
        result = cursor.fetchone()
        assert result is not None

        # Test insert
        wrapper.insert(
            "project_tbl", ["name", "language", "complete"], ["test", "python", 0]
        )

        # Test select
        projects = wrapper.select("project_tbl", ["*"])
        assert len(projects) == 1
        assert projects[0]["name"] == "test"
        assert projects[0]["language"] == "python"

        # Test exists
        assert wrapper.exists("project_tbl", "name='test'")
        assert not wrapper.exists("project_tbl", "name='nonexistent'")

        wrapper.close()
    finally:
        Path(db_path).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__])
