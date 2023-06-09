'''
@author jasperan
This file uses mljar-supervised to produce a preliminary ML report
'''

import pandas as pd
from sklearn.model_selection import train_test_split
from supervised import AutoML
import warnings
warnings.filterwarnings("ignore")


df = pd.read_csv(
    "performance_report.csv",
    skipinitialspace=True,
)

# We can use the train_test_split function from sklearn.model_selection to divide the df into training and testing sets.
# We will use 80% of the data for training and 20% for testing.

# To split the dataframe into training and testing sets, we will use the train_test_split function from sklearn.model_selection library.

train, test = train_test_split(df, test_size=0.2)

y = df.pop('win')
X = df
X = X.drop(columns=['f1', 'f2', 'f3', 'f4', 'f5', 'calculated_player_performance'], axis=1)
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2)

print(len(X_train), len(X_test), len(y_train), len(y_test))

automl = AutoML(mode="Compete", results_path="simple_regressor_complete_perform_unchained_1_full",
        algorithms=["Baseline", "Linear", "Decision Tree", "Random Forest", "Extra Trees",
            "LightGBM", "Xgboost", "CatBoost", "Neural Network", "Nearest Neighbors"],
        golden_features=True, features_selection=True,
        top_models_to_improve=5,
        train_ensemble=True,
        stack_models=True,
        start_random_models=10,
        explain_level=2,
        total_time_limit=96*3600)  # total time limit, set large enough to have time to compute all steps (4 days)


automl.fit(X_train, y_train)

predictions = automl.predict(X_test)
print(predictions[:5])


'''
automl = AutoML(
    mode='Explain',
    algorithms=["Baseline", "Linear", "Decision Tree", "Random Forest", "Extra Trees", "LightGBM", "Xgboost", "CatBoost", "Neural Network", "Nearest Neighbors"],
    model_time_limit=15*60,
    start_random_models=10,
    #hill_climbing_steps=3,
    top_models_to_improve=3,
    golden_features=True,
    features_selection=True,
    stack_models=True,
    train_ensemble=True,
    #explain_level=0,
    validation_strategy={
        "validation_type": "kfold",
        "k_folds": 4,
        "shuffle": False,
        "stratify": True,
    })
'''
