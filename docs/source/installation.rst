Installation
============

This section covers how to install the League of Legends Optimizer.

Prerequisites
------------

Before installing the League of Legends Optimizer, ensure you have the following prerequisites:

- Python 3.8 or higher
- Oracle Instant Client (optional, for Oracle database support)
- RabbitMQ server (for message queue support)
- Riot Games API key

Installing with Poetry (Recommended)
-----------------------------------

The recommended way to install the League of Legends Optimizer is using Poetry, which handles dependencies and virtual environments automatically.

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/oracle-devrel/leagueoflegends-optimizer.git
      cd leagueoflegends-optimizer

2. Install dependencies with Poetry:

   .. code-block:: bash

      poetry install

3. Activate the virtual environment:

   .. code-block:: bash

      poetry shell

Installing with pip
-----------------

You can also install the League of Legends Optimizer using pip:

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/oracle-devrel/leagueoflegends-optimizer.git
      cd leagueoflegends-optimizer

2. Install the package:

   .. code-block:: bash

      pip install -e .

Installing with Docker
--------------------

For a containerized installation, you can use Docker:

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/oracle-devrel/leagueoflegends-optimizer.git
      cd leagueoflegends-optimizer

2. Build and run with Docker Compose:

   .. code-block:: bash

      docker-compose up

Using the Setup Script
--------------------

The project includes a setup script that automates the installation process:

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/oracle-devrel/leagueoflegends-optimizer.git
      cd leagueoflegends-optimizer

2. Run the setup script:

   .. code-block:: bash

      bash setup.sh

The setup script will:

- Check if Python 3.8+ is installed
- Install Poetry if it's not already installed
- Install dependencies
- Create a config.yaml file if it doesn't exist
- Create necessary directories
- Activate the virtual environment

Next Steps
---------

After installation, you need to:

1. Obtain a Riot Games API key from the `Riot Developer Portal <https://developer.riotgames.com/>`_
2. Configure the application (see :doc:`configuration`)
3. Start using the application (see :doc:`usage`) 