Usage
=====

This section covers how to use the League of Legends Optimizer.

Command-Line Interface
---------------------

The League of Legends Optimizer provides a command-line interface (CLI) with various subcommands for different functionality.

Basic Usage
~~~~~~~~~~

.. code-block:: bash

    leagueoptimizer [COMMAND] [OPTIONS]

Available Commands
~~~~~~~~~~~~~~~~

Player List
^^^^^^^^^^^

Get players above masters' elo in all regions:

.. code-block:: bash

    leagueoptimizer player-list

Match List
^^^^^^^^^

Get match IDs for players:

.. code-block:: bash

    leagueoptimizer match-list

Match Download
^^^^^^^^^^^^

Download match data:

.. code-block:: bash

    leagueoptimizer match-download

For detailed match data:

.. code-block:: bash

    leagueoptimizer match-download --detail

Process Predictor
^^^^^^^^^^^^^^^

Process data for prediction:

.. code-block:: bash

    leagueoptimizer process-predictor

For live client prediction:

.. code-block:: bash

    leagueoptimizer process-predictor --live-client

Live Client Producer
^^^^^^^^^^^^^^^^^^

Start the live client producer:

.. code-block:: bash

    leagueoptimizer live-client-producer --ip localhost

Live Client Consumer
^^^^^^^^^^^^^^^^^^

Start the live client consumer:

.. code-block:: bash

    leagueoptimizer live-client-consumer --ip localhost -p /path/to/model

Visualizer
^^^^^^^^^

Start the game data visualizer:

.. code-block:: bash

    leagueoptimizer visualizer --host 0.0.0.0 --port 5000

All Commands
^^^^^^^^^^^

Run all commands in sequence:

.. code-block:: bash

    leagueoptimizer all

Web Visualization
---------------

The League of Legends Optimizer includes a web-based visualization interface for viewing game data and predictions.

Starting the Visualizer
~~~~~~~~~~~~~~~~~~~~~

1. Start the visualizer:

   .. code-block:: bash

      leagueoptimizer visualizer

2. Open a web browser and navigate to ``http://localhost:5000``

3. Start a League of Legends game and run the live client producer:

   .. code-block:: bash

      leagueoptimizer live-client-producer

4. The visualization will update in real-time with game data and predictions.

Visualization Features
~~~~~~~~~~~~~~~~~~~~

The web visualization provides the following features:

- 3D view of the game state
- Win probability prediction
- Player statistics
- Team composition analysis

Real-Time Prediction
------------------

To make real-time predictions during a League of Legends game:

1. Start the RabbitMQ server:

   .. code-block:: bash

      docker-compose up rabbitmq

2. Start the live client producer on the machine where you're playing League of Legends:

   .. code-block:: bash

      leagueoptimizer live-client-producer --ip RABBITMQ_IP_ADDRESS

3. Start the live client consumer:

   .. code-block:: bash

      leagueoptimizer live-client-consumer --ip RABBITMQ_IP_ADDRESS -p /path/to/model

4. Start a League of Legends game.

5. The consumer will make predictions based on the game data sent by the producer.

Docker Deployment
---------------

You can deploy the League of Legends Optimizer using Docker:

.. code-block:: bash

    docker-compose up

This will start the following services:

- ``rabbitmq``: RabbitMQ message broker
- ``visualizer``: Web visualization interface
- ``producer``: Live client data producer
- ``consumer``: Live client data consumer

You can also start specific services:

.. code-block:: bash

    docker-compose up rabbitmq visualizer

Or run in detached mode:

.. code-block:: bash

    docker-compose up -d

To stop the services:

.. code-block:: bash

    docker-compose down

Python API
--------

You can also use the League of Legends Optimizer as a Python library:

.. code-block:: python

    from leagueoptimizer.api.riot_client import riot_client
    from leagueoptimizer.api.live_client import LiveClientAPI
    from leagueoptimizer.data.database import db
    from leagueoptimizer.utils.message_queue import get_message_queue

    # Get summoner information
    summoner = riot_client.get_summoner_by_name("PlayerName", "euw1")

    # Get live game data
    live_client = LiveClientAPI()
    game_data = live_client.get_all_game_data()

    # Connect to the database
    db.connect()

    # Use the message queue
    queue = get_message_queue("my_queue")
    queue.connect()
    queue.publish({"key": "value"}) 