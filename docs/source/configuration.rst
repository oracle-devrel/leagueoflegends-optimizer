Configuration
=============

The League of Legends Optimizer can be configured using a YAML configuration file or environment variables.

Configuration File
----------------

The primary method of configuration is through a ``config.yaml`` file in the root directory of the project. Here's an example configuration file:

.. code-block:: yaml

    riot_api:
      key: RGAPI-xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx
      regions:
        - br1
        - eun1
        - euw1
        - jp1
        - kr
        - la1
        - la2
        - na1
        - oc1
        - ru
        - tr1

    database:
      type: sqlite  # oracle, sqlite, mock
      username: xxxxxx  # Only for Oracle
      password: xxxxxx  # Only for Oracle
      dsn: xxxx  # Only for Oracle
      sqlite_path: data/league.db  # Path for SQLite database

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
      save_path: models/trained

Configuration Sections
---------------------

Riot API
~~~~~~~~

The ``riot_api`` section configures the Riot Games API client:

- ``key``: Your Riot Games API key
- ``regions``: List of regions to use for data extraction

Database
~~~~~~~~

The ``database`` section configures the database connection:

- ``type``: The database type (``oracle``, ``sqlite``, or ``mock``)
- ``username``: The database username (Oracle only)
- ``password``: The database password (Oracle only)
- ``dsn``: The database DSN (Oracle only)
- ``sqlite_path``: The path to the SQLite database file

Message Queue
~~~~~~~~~~~~

The ``message_queue`` section configures the RabbitMQ connection:

- ``host``: The RabbitMQ host
- ``port``: The RabbitMQ port
- ``username``: The RabbitMQ username
- ``password``: The RabbitMQ password
- ``queue_name``: The name of the queue to use
- ``heartbeat``: The heartbeat interval in seconds
- ``blocked_connection_timeout``: The blocked connection timeout in seconds

Live Client
~~~~~~~~~~

The ``live_client`` section configures the Live Client Data API client:

- ``base_url``: The base URL for the Live Client Data API
- ``request_interval``: The interval between requests in seconds

Model
~~~~~

The ``model`` section configures the machine learning model:

- ``save_path``: The path to save trained models

Environment Variables
-------------------

You can also configure the application using environment variables. Environment variables take precedence over the configuration file.

Here are the available environment variables:

.. code-block:: bash

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

Configuration Precedence
----------------------

The configuration is loaded in the following order, with later sources taking precedence:

1. Default values
2. Configuration file (``config.yaml``)
3. Environment variables

This means that if you set a value in both the configuration file and an environment variable, the environment variable will be used.

Accessing Configuration in Code
-----------------------------

You can access the configuration in your code using the ``CONFIG`` object:

.. code-block:: python

    from leagueoptimizer.config.settings import CONFIG

    # Access configuration values
    api_key = CONFIG["riot_api"]["key"]
    db_type = CONFIG["database"]["type"] 