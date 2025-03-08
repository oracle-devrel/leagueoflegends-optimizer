# Contributing to League of Legends Optimizer

Thank you for your interest in contributing to the League of Legends Optimizer project! This document provides guidelines and instructions for contributing.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/oracle-devrel/leagueoflegends-optimizer.git
   cd leagueoflegends-optimizer
   ```

2. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

4. Create a `config.yaml` file with your Riot API key:
   ```yaml
   riot_api:
     key: YOUR_API_KEY
   ```

## Code Style

This project uses the following tools for code quality:

- **Black**: For code formatting
- **isort**: For import sorting
- **flake8**: For linting
- **mypy**: For static type checking

You can run these tools with the following commands:

```bash
# Format code with Black
black leagueoptimizer

# Sort imports with isort
isort leagueoptimizer

# Lint with flake8
flake8 leagueoptimizer

# Type check with mypy
mypy leagueoptimizer
```

## Running Tests

Run the tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=leagueoptimizer

# Run specific test file
pytest leagueoptimizer/tests/test_config.py

# Run tests with specific marker
pytest -m unit
```

## Project Structure

```
leagueoptimizer/
├── api/                  # API clients
│   ├── riot_client.py    # Riot Games API client
│   └── live_client.py    # Live Client Data API
├── config/               # Configuration management
│   └── settings.py       # Configuration loader
├── data/                 # Data extraction and processing
│   ├── player_list.py    # Player extraction
│   ├── match_list.py     # Match ID extraction
│   └── match_download.py # Match data download
├── models/               # ML model training and prediction
│   └── trained/          # Trained model storage
├── utils/                # Utility modules
│   ├── logging.py        # Logging configuration
│   ├── database.py       # Database abstraction
│   └── message_queue.py  # Message queue abstraction
├── visualization/        # Visualization modules
│   └── web_app.py        # Web visualization
└── cli.py                # Command-line interface
```

## Pull Request Process

1. Fork the repository and create a new branch for your feature or bug fix.
2. Make your changes, following the code style guidelines.
3. Add tests for your changes.
4. Run the tests to ensure they pass.
5. Update the documentation if necessary.
6. Submit a pull request with a clear description of the changes.

## Commit Message Guidelines

Please follow these guidelines for commit messages:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## Adding New Features

When adding new features, please follow these guidelines:

1. **Configuration**: Add any new configuration options to `config/settings.py` with appropriate default values.
2. **Documentation**: Update the README.md and add docstrings to your code.
3. **Testing**: Add tests for your new feature.
4. **Type Hints**: Add type hints to all functions and methods.
5. **Error Handling**: Implement proper error handling with custom exceptions if necessary.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's license (UPL-1.0). 