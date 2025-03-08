Model Training
=============

This section covers how to train machine learning models for the League of Legends Optimizer.

Overview
--------

The League of Legends Optimizer uses AutoGluon to train machine learning models for predicting game outcomes. AutoGluon is an AutoML framework that automatically trains and tunes a diverse set of models.

Training Process
--------------

The training process involves the following steps:

1. Load the preprocessed data
2. Split the data into training and validation sets
3. Define the target variable and features
4. Train the model using AutoGluon
5. Evaluate the model performance
6. Save the trained model

Example
-------

Here's an example of how to train a model using AutoGluon:

.. code-block:: python

    import pandas as pd
    from autogluon.tabular import TabularPredictor

    # Load the preprocessed data
    data = pd.read_csv('processed_data.csv')

    # Split the data into features and target
    X = data.drop('win', axis=1)
    y = data['win']

    # Train the model
    save_path = 'models/trained'
    predictor = TabularPredictor(label='win', path=save_path).fit(
        train_data=data,
        time_limit=3600,  # 1 hour
        presets='best_quality'
    )

    # Evaluate the model
    evaluation = predictor.evaluate(data)
    print(evaluation)

    # Make predictions
    predictions = predictor.predict(X)
    probabilities = predictor.predict_proba(X)

Available Models
--------------

AutoGluon automatically trains and tunes a variety of models, including:

- Random Forest
- Gradient Boosting (XGBoost, LightGBM, CatBoost)
- Neural Networks
- K-Nearest Neighbors
- Linear Models
- Extra Trees
- And more

Hyperparameter Tuning
-------------------

AutoGluon automatically tunes the hyperparameters of the models. You can control the time limit for training using the `time_limit` parameter:

.. code-block:: python

    predictor = TabularPredictor(label='win', path=save_path).fit(
        train_data=data,
        time_limit=3600,  # 1 hour
        presets='best_quality'
    )

Model Stacking
------------

AutoGluon uses model stacking to combine the predictions of multiple models. This often leads to better performance than any single model.

The stacking process involves:

1. Training multiple base models
2. Using the predictions of these models as features for a higher-level model
3. Repeating this process for multiple levels

Saving and Loading Models
----------------------

You can save and load models using the following methods:

.. code-block:: python

    # Save the model
    predictor.save()

    # Load the model
    from autogluon.tabular import TabularPredictor
    loaded_predictor = TabularPredictor.load('models/trained')

    # Make predictions with the loaded model
    predictions = loaded_predictor.predict(X)

Feature Importance
---------------

You can analyze feature importance to understand which features are most important for the model:

.. code-block:: python

    # Get feature importance
    importance = predictor.feature_importance(data)
    print(importance)

    # Plot feature importance
    import matplotlib.pyplot as plt
    importance.plot(kind='barh', figsize=(10, 8))
    plt.title('Feature Importance')
    plt.show()

Next Steps
---------

After training the model, you can:

- Evaluate the model on a test set (see :doc:`evaluation`)
- Deploy the model for real-time predictions (see :doc:`deployment`)
- Use the model in the League of Legends Optimizer (see :doc:`../usage`) 