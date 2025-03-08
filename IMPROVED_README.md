# League of Legends Optimizer (Improved)

A tool for predicting League of Legends game outcomes in real-time using machine learning.

## Features

- Extract data from professional players using the Riot Games API
- Store data in various database backends (Oracle, SQLite)
- Train machine learning models to predict game outcomes
- Make real-time predictions during games using the Live Client Data API
- Visualize game data and predictions with a 3D web interface
- Modern package structure with proper dependency management
- Comprehensive error handling and logging
- Configurable through environment variables or config files
- Docker support for easy deployment

## Architecture

The improved architecture includes:

- Modular code structure with proper package organization
- Abstraction layers for database and message queue operations
- Improved error handling and logging
- Configuration management system
- Command-line interface with subcommands
- Web visualization using Three.js
- Docker support for easy deployment

## Installation

### Prerequisites

- Python 3.8 or higher
- Oracle Instant Client (optional, for Oracle database support)
- RabbitMQ server (for message queue support)
- Riot Games API key

### Using Poetry (recommended)

```bash
# Clone the repository
git clone https://github.com/oracle-devrel/leagueoflegends-optimizer.git
cd leagueoflegends-optimizer

# Install dependencies with Poetry
poetry install

# Activate the virtual environment
poetry shell
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/oracle-devrel/leagueoflegends-optimizer.git
cd leagueoflegends-optimizer

# Install the package
pip install -e .
```

### Using Docker

```bash
# Clone the repository
git clone https://github.com/oracle-devrel/leagueoflegends-optimizer.git
cd leagueoflegends-optimizer

# Build and run with Docker Compose
docker-compose up
```

## Configuration

Create a `config.yaml` file in the root directory with your Riot Games API key and other settings:

```yaml
riot_api:
  key: RGAPI-xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx

database:
  type: sqlite  # oracle, sqlite, mock
  username: xxxxxx  # Only for Oracle
  password: xxxxxx  # Only for Oracle
  dsn: xxxx  # Only for Oracle

message_queue:
  host: localhost
  port: 5672
  username: league
  password: league
  queue_name: live_client
  heartbeat: 600
  blocked_connection_timeout: 300

live_client:
  base_url: https://127.0.0.1:2999/liveclientdata
  request_interval: 30  # seconds

model:
  save_path: /path/to/models/trained
```

Alternatively, you can set environment variables:

```bash
export RIOT_API_KEY=RGAPI-xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx
export DB_TYPE=sqlite
export DB_USERNAME=xxxxxx
export DB_PASSWORD=xxxxxx
export DB_DSN=xxxx
export MQ_HOST=localhost
export MQ_PORT=5672
export MQ_USERNAME=league
export MQ_PASSWORD=league
export MODEL_SAVE_PATH=/path/to/models/trained
```

## Usage

### Command-Line Interface

The package provides a command-line interface with various subcommands:

```bash
# Get players above masters' elo in all regions
leagueoptimizer player-list

# Get match IDs for players
leagueoptimizer match-list

# Download match data
leagueoptimizer match-download
leagueoptimizer match-download --detail  # Detailed match data

# Process data for prediction
leagueoptimizer process-predictor
leagueoptimizer process-predictor --live-client  # For live client prediction

# Start the live client producer
leagueoptimizer live-client-producer --ip localhost

# Start the live client consumer
leagueoptimizer live-client-consumer --ip localhost -p /path/to/model

# Start the game data visualizer
leagueoptimizer visualizer --host 0.0.0.0 --port 5000

# Run all commands in sequence
leagueoptimizer all
```

### Web Visualization

The web visualization provides a 3D view of the game state and predictions:

1. Start the visualizer:
   ```bash
   leagueoptimizer visualizer
   ```

2. Open a web browser and navigate to `http://localhost:5000`

3. Start a League of Legends game and run the live client producer:
   ```bash
   leagueoptimizer live-client-producer
   ```

4. The visualization will update in real-time with game data and predictions.

## Development

### Project Structure

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

### Key Components

#### Configuration Management

The configuration system (`config/settings.py`) loads settings from:
1. Default values
2. Config file (config.yaml)
3. Environment variables (highest priority)

```python
# Load configuration
from leagueoptimizer.config.settings import CONFIG

# Access configuration values
api_key = CONFIG["riot_api"]["key"]
db_type = CONFIG["database"]["type"]
```

#### Logging

The logging system (`utils/logging.py`) provides consistent logging across the application:

```python
# Get a logger
from leagueoptimizer.utils.logging import get_logger
logger = get_logger("my_module", level="debug", log_file="my_module.log")

# Use the logger
logger.info("This is an info message")
logger.error("This is an error message")
```

#### Database Abstraction

The database abstraction layer (`data/database.py`) supports multiple database backends:

```python
# Get the database instance
from leagueoptimizer.data.database import db

# Connect to the database
db.connect()

# Execute a query
db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")

# Insert data
db.insert("users", {"name": "John"})

# Query data
users = db.fetch_all("SELECT * FROM users")

# Disconnect
db.disconnect()
```

#### Message Queue

The message queue system (`utils/message_queue.py`) provides a reliable way to communicate between components:

```python
# Get a message queue instance
from leagueoptimizer.utils.message_queue import get_message_queue
queue = get_message_queue("my_queue")

# Connect to the queue
queue.connect()

# Publish a message
queue.publish({"key": "value"})

# Consume messages
def process_message(message):
    print(f"Received: {message}")

queue.consume(process_message)

# Disconnect
queue.disconnect()
```

#### API Clients

The API clients (`api/riot_client.py` and `api/live_client.py`) provide access to external APIs:

```python
# Riot API client
from leagueoptimizer.api.riot_client import riot_client

# Get summoner information
summoner = riot_client.get_summoner_by_name("PlayerName", "euw1")

# Live Client API
from leagueoptimizer.api.live_client import LiveClientAPI
live_client = LiveClientAPI()

# Get game data
game_data = live_client.get_all_game_data()
```

#### Web Visualization

The web visualization (`visualization/web_app.py`) provides a 3D view of the game state:

```python
# Start the visualizer
from leagueoptimizer.visualization.web_app import start_visualizer
start_visualizer(host="0.0.0.0", port=5000, debug=True)
```

### Running Tests

```bash
# Run tests with pytest
pytest

# Run tests with coverage
pytest --cov=leagueoptimizer
```

## Docker Deployment

The project includes Docker support for easy deployment:

```bash
# Build and run with Docker Compose
docker-compose up

# Run specific services
docker-compose up rabbitmq visualizer

# Run in detached mode
docker-compose up -d

# Stop services
docker-compose down
```

The Docker Compose setup includes the following services:
- `rabbitmq`: RabbitMQ message broker
- `visualizer`: Web visualization interface
- `producer`: Live client data producer
- `consumer`: Live client data consumer

## License

Copyright (c) 2022 Oracle and/or its affiliates.

Licensed under the Universal Permissive License (UPL), Version 1.0.

See LICENSE for more details.

## Changelog

### v0.1.0 (Current)

#### Code Structure and Organization
- Created a proper Python package structure with `leagueoptimizer/` as the main package
- Modularized the codebase into logical components (api, config, data, models, utils, visualization)
- Set up modern dependency management with Poetry
- Added proper type hints throughout the codebase

#### Quality Improvements
- Added comprehensive logging with proper formatters and handlers
- Implemented consistent error handling patterns
- Added support for automated testing with pytest
- Added code formatting configuration (black, isort)
- Added static type checking with mypy

#### Architecture Enhancements
- Implemented database abstraction layer with support for Oracle, SQLite, and mock databases
- Improved message queue implementation with error handling and dead letter queues
- Created a centralized configuration system with support for environment variables and config files
- Implemented a command-line interface with subcommands

#### Visualization and Deployment
- Created a web visualization using Flask and Three.js
- Added Docker support with multi-service setup
- Created a Docker Compose configuration for easy deployment
- Added comprehensive documentation 