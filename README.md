# Walter

![Language](https://img.shields.io/github/languages/top/Aazerra/Walter.svg?style=for-the-badge&logo=python) ![License](https://img.shields.io/github/license/Aazerra/Walter?style=for-the-badge)

## The purpose of this project

Walter is a modern Project Manager and Project generator that helps developers quickly scaffold new projects in various programming languages with proper directory structure and basic boilerplate code.

## Features

- **Multi-language support**: Python, Node.js, Go, PHP, and Lua
- **Smart project scaffolding**: Creates appropriate project structure for each language
- **Project tracking**: Track project completion status
- **Modern architecture**: Built with type hints, design patterns, and best practices
- **Poetry-based dependency management**: Modern Python packaging and dependency management

## Installation

### Using Poetry (Recommended)

```bash
git clone https://github.com/Aazerra/Walter.git
cd Walter
poetry install
```

### Development Setup

```bash
# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .

# Type checking
poetry run mypy walter/
```

## Usage

### Create a new project
```bash
# Create a Python project
walter -p my-python-app create -l python

# Create a Node.js project  
walter -p my-node-app create -l node

# Create a Go project
walter -p my-go-app create -l go
```

### List all projects
```bash
walter list
```

### Mark project status
```bash
# Mark as complete
walter -p my-app mark com

# Mark as incomplete
walter -p my-app mark incom
```

## Supported Languages

- **Python**: Creates virtual environment, requirements.txt, and main.py
- **Node.js**: Initializes with yarn, creates package.json and index.js
- **Go**: Initializes Go module and creates main.go
- **PHP**: Creates index.php and optional composer setup
- **Lua**: Creates main.lua file

## Architecture

Walter now uses modern software design patterns:

- **Strategy Pattern**: For different project creation strategies
- **Factory Pattern**: For creating project creators
- **Dependency Injection**: For better testability
- **Type Hints**: Full type coverage for better IDE support
- **Protocol-based Design**: For database abstraction

## who is Walter?

Walter is my hero from [Fringe](https://www.imdb.com/title/tt1119644) TV series
Walter is a funny scientist

<h1 align="center">
	<img width="300" src="images/walter.jpg" alt="walter">
	<br>
</h1>
