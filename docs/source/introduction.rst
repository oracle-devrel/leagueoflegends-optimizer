Introduction
============

League of Legends Optimizer is a project created for educational purposes that uses Riot Games' API to make real-time predictions in game. The project is able to extract data from professional players, store this information in various database backends, and use this data to train ML models to accurately predict the winning probability of a player.

Project Overview
---------------

League of Legends is one of the most popular multiplayer online battle arena (MOBA) games in the world. In each match, two teams of five players compete to destroy the opposing team's base. Each player controls a "champion" with unique abilities and plays a specific role within their team.

This project aims to:

1. Extract data from professional players using the Riot Games API
2. Store and process this data for machine learning
3. Train models to predict game outcomes
4. Make real-time predictions during games
5. Visualize the predictions and game state

Data Sources
-----------

The project uses two main data sources:

1. **Riot Games API**: This official API provides access to match history, player statistics, and other game data. We use this to collect training data from professional players.

2. **Live Client Data API**: This API provides real-time data during a game. We use this to make predictions while a game is in progress.

Machine Learning Approach
------------------------

The project uses a combination of traditional machine learning and AutoML techniques to predict game outcomes. The main steps in our ML pipeline are:

1. **Data Collection**: Gathering match data from professional players
2. **Feature Engineering**: Extracting relevant features from the raw data
3. **Model Training**: Using AutoGluon to train and optimize models
4. **Evaluation**: Assessing model performance with appropriate metrics
5. **Deployment**: Making the model available for real-time predictions

Architecture
-----------

The project follows a modular architecture with the following components:

- **API Clients**: For interacting with Riot Games API and Live Client Data API
- **Data Processing**: For extracting, transforming, and loading data
- **Database Abstraction**: For storing data in various backends
- **Machine Learning**: For training and making predictions
- **Visualization**: For displaying predictions and game state
- **Message Queue**: For communication between components

Getting Started
--------------

To get started with the League of Legends Optimizer, see the :doc:`installation` and :doc:`usage` sections. 