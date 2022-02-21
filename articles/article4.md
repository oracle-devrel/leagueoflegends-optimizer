# League of Legends Optimizer using Oracle Cloud Infrastructure: Real-Time predictions

## Recap and Introduction
Welcome to the third article of the League of Legends Optimizer series!

In this article, we're diving deep into building a classifier model to predict the winner of two champion matchups withs Oracle Cloud Infrastructure (OCI).

In previous articles, we've done the following:

- [x] Defined and modelled our problem, understanding the different steps in the drafting phase of the game
- [x] Explored the various endpoints offered by Riot Games in their official API
- [x] Pulled data from the most skilled players around the world and built a data set of these players, which left us with a structure like this in our non-relational autonomous database
- [x] Created data structures, such as the *matchup* structure, to represent the data we pulled from the API in an adversarial way: in this data structure (see [this dataset](https://www.kaggle.com/jasperan/league-of-legends-1v1-matchups-results)), we faced each lane in a game against the enemy's, and determined whether this player won or lost the game.

Following this data structure, we're going to make a reliable model that can predict the best champion to pick against another player using by using machine learning.

## The Data Structure

From the [Kaggle dataset](https://www.kaggle.com/jasperan/league-of-legends-1v1-matchups-results), we see an example of the data structure we're going to use to build our model:

```json 
{
    "p_match_id": "BR1_2133948485_bottom",
    "data": [
        {
            "goldEarned": 10767,
            "totalMinionsKilled": 161,
            "win": false,
            "kills": 6,
            "assists": 8,
            "deaths": 6,
            "champion": "Kayle",
            "visionScore": 14,
            "puuid": "s1j7_icmqQCl1vROjASKJLSGZmktnvcrt8Qm7g39T16YdxE-xTlX2nnrG400bMae7O3JWyf2Y4XX4Q",
            "totalDamageDealtToChampions": 13008,
            "summonerName": "EveBy"
        },
        {
            "goldEarned": 14787,
            "totalMinionsKilled": 172,
            "win": true,
            "kills": 14,
            "assists": 2,
            "deaths": 6,
            "champion": "Kaisa",
            "visionScore": 12,
            "puuid": "zjBoj6G9dWbPgkKSvZpDIcDA2NG65M1FUOxlYCXUyff9I1GR_xIuOFLWXlzMjWV67gOnGFC7g6wCuw",
            "totalDamageDealtToChampions": 23071,
            "summonerName": "Goiasinho"
        }
    ],
    "gameVersion": "10.25.348.1797"
}
```

The intricacies of how we built the data structure and derived the result from it are explained in the [previous article](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/main/articles/article2.md). It is important to remember that structuring and manipulating data in the data science process takes an average of 80 to 90% of the time, according to expert sources (image courtesy of [“2020 State of Data Science: Moving From Hype Toward Maturity.”](https://www.anaconda.com/state-of-data-science-2020)), and we shouldn't be discouraged when spending most of our time processing and manipulating data structures. The ML algorithm is the easy part if you've correctly identified the correct data structure and adapted it to the structure ML algorithms expect.

{% imgx assets/lol-3-anaconda_1.png "Breakdown of effort to train model" %}

For our first model, we're going to simplify the present data structure even more and get something like this:

```json
{
    "match_id": "EUN1_2910807891_utility",
    "champ1": "Velkoz",
    "champ2": "Yuumi",
    "win": 1
}
```

Where `win` is a boolean variable that represents whether `champ1` won or not. So, in this example, Velkoz won the game.

If we analyze this data structure, we see that it's very simplistic and only contains three useful variables (having excluded the identifier variable, which is only there to ensure we don't have duplicate values in our JSON database). One of these variables is actually the result of the game and the feature that we'd like to predict. This can have two different implications:
- The model is simple and works because the problem is simple. I suggest always trying this out regardless of the prediction problem and checking if the model is actually able to make accurate predictions.
- The model doesn't work because we oversimplified the problem and there are many more variables to consider to make improvements on model accuracy. This is most likely the case in many real-world problems, in which I also include our League of Legends Optimizer. So, probably, this initial ML model will not have great predictions. Nonetheless, we'll try anyway with what we currently have.

## The Code

We begin with simple data exploration of our initial dataset.

```python
import pandas as pd
pd.set_option('float_format', '{:f}'.format)
import os
import seaborn as sns
import matplotlib.pyplot as plt
%matplotlib inline

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler 
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

df = pd.read_json('data_location.json') # we've stored the data file locally in this case
df.head(5)
```

| match_id	| champ1 | champ2 |	win |
| :----------:	| :------:	| :------:	| :----: |
| EUN1_2910807891_utility |	Velkoz | Yuumi | 1 |
| EUN1_2910807891_jungle | Shaco |	Nidalee	| 1 |
| EUN1_2909987530_top | Riven |	Sett |	0 |
| EUN1_2909987530_middle | Lissandra |	Kassadin |	0 |
| EUN1_2909987530_bottom | Ashe | Ezreal | 0 |

In this simple model, there is almost no need for data exploration since we fully understand what each variable means, as they are by-products of our initial data structure.

We split our data into train-test sets:

```python
# We want to predict the 'win' variable.
train_features = train_dataset.copy()
test_features = test_dataset.copy()

train_labels = train_features.pop('win') # returns column 'win'
test_labels = test_features.pop('win') # returns column 'win'
```

We encode the data following the Data Science process:

```python
le = LabelEncoder()

le = le.fit(champ_list) # fit the label encoder with the whole champion list.

train_features = train_features.apply(lambda x: le.transform(x))
test_features = test_features.apply(lambda x: le.transform(x))
```

Note that the `champ_list` referenced in this code block is the list of all unique champions in LoL.

We need to fit our label encoder with all possible values. Otherwise, new values will not be properly encoded or may be encoded as a duplicate number.

```python
# Normalization
scaler = StandardScaler()
train_features = scaler.fit_transform(train_features)
test_features = scaler.transform(test_features)
```

After scaling the data we can fit our model:

```python
logreg = LogisticRegression()
logreg.fit(train_features, train_labels)
print('Accuracy of Logistic regression classifier on training set: {:.2f}'
     .format(logreg.score(train_features, train_labels)))
print('Accuracy of Logistic regression classifier on test set: {:.2f}'
     .format(logreg.score(test_features, test_labels)))
```

The accuracies obtained for the logistic regression classifier are 0.51. This is like tossing a coin. We could be making better assumptions by having a bit of knowledge about the game and champion performances. So our hypothesis saying that this simplistic model would not work correctly is correct. We need to improve our model or add variables to it.

However, we can still make predictions using our model. The code to make a prediction needs to consider new data, encode it and scale it, and then make a prediction:

```python
new_data = {
    'champ1': ['Xayah', 'Karma', 'Xerath', 'Gragas', 'Chogath'],
    'champ2': ['Tristana', 'Lulu', 'Syndra', 'Sejuani', 'Gnar']
}
new_df = pd.DataFrame(new_data)
```

In this case, as our model is very limited in regards to input variables, we make the following assumption: we'll calculate a team winning by taking the mode of all lanes' predictions.

Let's transform our data:

```python
new_df = new_df.apply(lambda x: le.transform(x))

new_df.tail(5)
```

| champ1 | champ2  |
| :---:	| :---:	|
| 143 | 126 |
| 52 | 69 |
| 144 | 119 |
| 36 | 104 |
| 19 | 35 |

As we can see, our champion input variables have been properly one-hot encoded. As these are the two only variables we have for our model, applying a standard scaler will not make a difference, since all variables have a standard deviation of 1 between each other (all champions are translated into distinct integer numbers).

If we make the prediction:

```python
result = logreg.predict(new_df)

def find_winner(lst):
    return max(set(lst), key=lst.count)

winner_prediction = find_winner(result.tolist())
```

> [0 0 0 0 0]

The results of the prediction indicate the predicted winning team in each case. In this case, it's predicting `champ2` to win in all five cases. This can be a coincidence or not, but it happens to be the correct prediction. In case of having discrepancies, we'd use the `find_winner()` function to find the mode of the prediction. Adding this to the ML model actually improves the implicit accuracy of our code, but not of the model itself: we're simply combining a 51% accuracy ML model with additional statistics to make a better prediction. 

We may ask ourselves how we can measure the accuracy of our combined ML-statistics model The problem is **we can't**, since we have no programming framework able to assist us with this. We'd have to code our own object-oriented programming framework that extends the functionalities of the current Pandas framework, for example. And the time required to do so greatly exceeds the expected results. It's better we focus our resources, as data scientists, to using the frameworks available to us with our structured data, and  finding a better model by improving the quality of our input data. No need to reinvent the wheel.

Finally, to see the results in a human-readable way, we need to apply the `inverse_transform()` function to our still-encoded data:

```python
inverse_prediction = new_df.apply(lambda x: le.inverse_transform(x)) # we apply inverse transform

if winner_prediction == 1:
    print('Predicted winner is team 1: \n{}'.format(str(inverse_prediction['champ1'])))
else:
     print('Predicted winner is team 2: \n{}'.format(str(inverse_prediction['champ2'])))
```

Now, we can see one prediction per case, totaling 5 cases, and one final team prediction using our `find_winner()`:

```console
Predicted winner is team 2: 
Tristana
Lulu
Syndra
Sejuani
Gnar
```

## Improving the model

As we've seen in practice, the accuracy of our model is not as good as it could be. We can improve it by adding more variables to our model. We're going to create a model that considers all variables in our *matchup* data structure, and reduce the complexity of our ML code by using AutoML open-source tools for data exploration and model training.

```python
from pandas_profiling import ProfileReport
df = pd.read_csv('matchups.csv')
report = ProfileReport(df)
report
```

This simple code generates a dynamic report that shows the data types, missing values, and other information about the data. We explore the Pearson's r correlation coefficient between the variables:

{% imgx assets/lol-3-pearson.png "Visualization of Pearson's r daya" %}

We proceed to train our model with all variables, taking into consideration that most of the variables in our model are highly correlated. This is especially true for the amount of gold earned with respect to the number of kills and minions killed (which makes sense, as these are two of the actions that give out the most gold in-game). We also see that the vision score highly correlates with the amount of assists a player makes in a game.

```python
from autogluon.tabular import TabularPredictor, TabularDataset
# train-test split
df = TabularDataset('matchups.csv')

train = df.sample(frac=0.8, random_state=200)
test = df.drop(train.index)

# a simple look into our data
df.head(2)
```

| P_MATCH_ID | 	GOLDEARNED | 	TOTALMINIONSKILLED | 	WIN | 	KILLS | 	ASSISTS | 	DEATHS | 	CHAMPION | 	VISIONSCORE | 	PUUID | 	TOTALDAMAGEDEALTTOCHAMPIONS | 	SUMMONERNAME | 	GAMEVERSION |
| :--------: | :----------: | :---------------------: | :----: | :-----: | :------: | :------: | :--------: | :---------: | :--------: | :--------: | :--------: | :--------: |
| BR1_2309470512_jungle | 7670 | 37 | False | 4 | 2 | 7 | Graves | 23 | b1ZVlTG630NWh8Hgc7H-_-SErq3E3OkV50XSBuz_uzkIuA... |11215 | tired blessed | 	11.14.385.9967 |
| EUN1_2809958230_top | 11108 | 202 | False | 1 | 9 | 8 | Gwen | 28 | 19ii6j4OOWmkUaw_yAXhMOhcgUvZaK8M1yVT0I3HwBYQka... | 17617 | ozzyDD 	| 11.8.370.4668 |

We determine our predicting feature and fit the model:

```python
label = 'WIN'

save_path = './trained_models'  # specifies folder to store trained models
predictor = TabularPredictor(label=label, path=save_path).fit(train)
```

We can now make predictions on our test data:

```python
y_test = test[label]  # predict 'WIN'
test_data_nolabel = test.drop(columns=[label]) 
test_data_nolabel.head()

predictor = TabularPredictor.load(save_path)
y_pred = predictor.predict(test_data_nolabel)
print("Predictions:  \n", y_pred)
perf = predictor.evaluate_predictions(y_true=y_test, y_pred=y_pred, auxiliary_metrics=True)
```

We can see some sample predictions by our model on the test data.

| row_id | win |
| :----: | :--: |  
| 2 | False |
| 4 | False |
| 8 | False |
| 13 | False |
| 21 | True |

And with all trained models, we create a leaderboard with descending accuracy:

```python
predictor.leaderboard(test, silent=True)
```

| model | score_test | score_val | pred_time_test | pred_time_val | fit_time | pred_time_test_marginal | pred_time_val_marginal | fit_time_marginal | stack_level | can_infer | fit_order |
| :----: | :---------: | :---------: | :-------------: | :-------------: | :--------: | :-------------: | :-------------: | :-------------: | :-------------: | :-------------: | :----------: |
| NeuralNetMXNet | 0.836975 |	0.836461 |	33.964055 | 2.709942 |	6597.902246 |	33.964055 |	2.709942 | 6597.902246 | 1 | True | 12 |
| NeuralNetFastAI | 0.835870 |	0.839318 |	5.002273 | 0.199540 |	823.687658 |	5.002273 | 0.199540 | 823.687658 | 	1 |	True |	10 |
| LightGBMXT |	0.835717 |	0.833317 | 	12.957499 | 0.471436 |	82.666493 | 	12.957499 |	0.471436 | 82.666493 | 	1	| True |	3 |
| LightGBMLarge | 0.835348 | 	0.831603 | 22.367250 | 1.271694 | 136.043589 | 22.367250 | 1.271694 | 136.043589 |	1 |	True |	13 |
| WeightedEnsemble_L2 | 0.833629 | 0.966949 | 53.280581 | 4.445315 | 7548.607457 | 0.009523 | 0.044953 | 8.442531 |	2 |	True |	14 |
| LightGBM | 0.832460 |	0.829127 | 5.237847 | 0.278245 | 57.027379 | 5.237847 | 0.278245 |	57.027379 |	1 |	True |	4 |
| RandomForestEntr | 0.824462 | 0.822840 | 21.206490 | 0.434653 | 396.571945 | 21.206490 |	0.434653 |	396.571945 |	1 |	True |	6 |
| RandomForestGini | 0.823243 | 0.821697 | 29.693281 | 0.436249 | 256.947097 | 29.693281 |	0.436249 |	256.947097 |	1 |	True |	5 |
| XGBoost |	0.823159 | 0.823602 | 2.646490 | 0.696468 |	27.096065 | 2.646490 | 0.696468 |	27.096065 |	1 |	True |	11 |
| ExtraTreesGini | 0.817348 | 0.817602 | 22.973135 | 0.235120 | 40.649245 | 22.973135 |	0.235120 |	40.649245 |	1 |	True |	8 |
| ExtraTreesEntr | 0.817314 | 0.817316 | 10.118013 | 0.233918 | 47.698864 | 10.118013 |	0.233918 |	47.698864 |	1 |	True |	9 |
| CatBoost | 0.789888 |	0.956377 | 1.347230 | 1.019444 | 35.908529 | 1.347230 |	1.019444 |	35.908529 |	1 |	True |	7 |
| KNeighborsUnif | 0.637996 | 0.641109 | 3.568800 | 0.234611 | 5.264223 | 3.568800 |	0.234611 |	5.264223 |	1 |	True |	1 |
| KNeighborsDist | 0.637668 | 0.640442 | 3.253163 | 0.237193 | 5.326229 | 3.253163 |	0.237193 |	5.326229 |	1 |	True |	2 |

As we can see, including more variables in the model greatly improved the accuracy and reduced MAE and MSE of our model. We can also see that the model is able to predict the outcome of the game in the test data given the features in our data structure. This proves that a simple model is not always the best solution. We can achieve better results by using more advanced models, in this case about 83% accuracy, which is pretty good for a real-world problem.

Also, note that we don't really care how the models are trained as long as they make good predictions. Of course, it's important to know the basics of ML to see how data is structured, but I'd like you, as a reader, to finish reading this article and remember that the hardest part about data science and data engineering is not coding the ML model, but understanding the data and the problem, and structuring the data accordingly to satisfy our needs.

## The Problem and Next Steps

In short, in the first model, we didn't consider enough variables. The results of this ML model were no better than using simple statistics, and heavily relied on additional statistics support to make a bit more sense.

After expanding the model further, we saw that the model could make predictions much more accurately. However, we needed to ask ourselves if this model is useful. Are we, as players of League of Legends, able to have this amount of data in the middle of a game? The answer is **no**. We're just given simple statistics like the gold from the team and KDA ratio. Only programatically through the API do we have the possibility to access all this data. So, while the model is pretty good, it doesn't have a practical side that we can use and take advantage of. This is what we'll explore in the fourth article in this series: integrating such a model (or a similar one) with data that we can actually use in real-time to make accurate predictions; data aligned with what players have at hand. Stay tuned for article 4!

## How can I get started on OCI?

Remember that you can always sign up for free with OCI! Your Oracle Cloud account provides a number of Always Free services and a Free Trial with US$300 of free credit to use on all eligible OCI services for up to 30 days. These Always Free services are available for an **unlimited** period of time. The Free Trial services may be used until your US$300 of free credits are consumed or the 30 days has expired, whichever comes first. You can [sign up here for free](https://signup.cloud.oracle.com/?source=:ex:tb:::::WWMK211125P00027&SC=:ex:tb:::::WWMK211125P00027&pcode=WWMK211125P00027).

## License

Written by [Ignacio Guillermo Martínez](https://www.linkedin.com/in/ignacio-g-martinez/) [@jasperan](https://github.com/jasperan)

Copyright (c) 2021 Oracle and/or its affiliates.

Licensed under the Universal Permissive License (UPL), Version 1.0.

See [LICENSE](../LICENSE) for more details.

