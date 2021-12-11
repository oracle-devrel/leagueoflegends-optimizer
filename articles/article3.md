# League of Legends Optimizer using Oracle Cloud Infrastructure: Building an Adversarial League of Legends AI Model

## Recap & Introduction
Welcome to the third article of the League of Legends Optimizer series. In this article, we're going to deep dive into building a classifier model to predict the winner of two champion matchups in Oracle Cloud Infrastructure.

In the previous articles, remember that we've already done the following:
- We defined and modelled our problem, understanding the different steps in the drafting phase of the game
- We explored the various endpoints offered by Riot Games in their official API
- We pulled data from the most skilled players around the world and built a data set of these players, which left us with a structure like this in our non-relational autonomous database
- We created data structures, such as the **matchup** structure, to represent the data we pulled from the API in an adversarial way: in this data structure (see [this dataset](https://www.kaggle.com/jasperan/league-of-legends-1v1-matchups-results)) we faced each lane in a game against the enemy's, and determined whether this player won or lost the game.

Following this data structure, we're going to attempt to make a reliable model that can predict the best champion to pick against each other using Machine Learning.

## The Data Structure

From the Kaggle dataset, we see an example of the data structure we're going to use to build our model:

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

The intricacies of how we built the data structure and derived the result from it are explained in the [previous article](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/main/articles/article2.md). It is important to remember that structuring and manipulating data in the Data Science process takes an average of 80 to 90% of the time, according to expert sources (image courtesy of [“2020 State of Data Science: Moving From Hype Toward Maturity.”](https://www.anaconda.com/state-of-data-science-2020)), and we should not be discouraged when spending most of our time processing and manipulating data structures. The ML algorithm is the easy part if you've correctly identified the correct data structure and adapted it to the structure ML algorithms expect.

https://2s7gjr373w3x22jf92z99mgm5w-wpengine.netdna-ssl.com/wp-content/uploads/2020/07/Anaconda_1.png


For our first model, we're going to simplify the present data structure even more and get something like this:

```json
{
    "match_id": "EUN1_2910807891_utility",
    "champ1": "Velkoz",
    "champ2": "Yuumi",
    "win": 1
}
```
where win is a boolean variable that represents whether champ1 won or not. So, in this example, Velkoz won the game.
If we analyze the above mentioned data structure, we see that it's very simplistic and only contains three useful variables (having excluded the identifier variable, which is only there to ensure we don't have duplicate values in our JSON database), one of which is actually the result of the game and the feature that we'd like to predict. This can have two different implications:
- The model is simple and works because the problem is simple. I suggest always trying this out regardless of the prediction problem and checking if the model is actually able to make accurate predictions.
- The model doesn't work because we oversimplified the problem and there are many more variables to consider to make improvements on model accuracy. This is most likely the case in many real-world problems, which I also include our League of Legends Optimizer in. So, probably, this initial ML model will not have great predictions. Nonetheless, we'll try anyway with what we currently have.

## The Code

We begin with simple data exploration of our initial dataset.

```python
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
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

df = pd.read_json('data_location.json') # we've stored the data file locally only, since we're expecting results not to be great.

df.head(5)
```
```
> match_id	champ1	champ2	win
> 0	EUN1_2910807891_utility	Velkoz	Yuumi	1
> 1	EUN1_2910807891_jungle	Shaco	Nidalee	1
> 2	EUN1_2909987530_top	Riven	Sett	0
> 3	EUN1_2909987530_middle	Lissandra	Kassadin	0
> 4	EUN1_2909987530_bottom	Ashe	Ezreal	0
```

In this simple model, there is almost no need for data exploration since we fully understand what each variable means, as it is a by-product of our initial data structure.

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
Note that the champ_list referenced in this code block is the list of all unique champions in LoL.
We need to fit our label encoder with all possible values, otherwise new values will not be properly encoded or encoded as a duplicate number.

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

The accuracies obtained for the logistic regression classifier are 0.51. This is like tossing a coin. We could be making better assumptions having a bit of knowledge about the game and champion performances. So, our hypothesis saying that this simplistic model would not work correctly, is correct. We need to improve our model or add variables to it.

However, we can still make predictions using our model. The code to make a prediction needs to consider new data, encode it and scale it, and then make a prediction:

```python
new_data = {
    'champ1': ['Xayah', 'Karma', 'Xerath', 'Gragas', 'Chogath'],
    'champ2': ['Tristana', 'Lulu', 'Syndra', 'Sejuani', 'Gnar']
}
new_df = pd.DataFrame(new_data)
```

In this case, as our model is very limited in regards to input variables, we make the following assumption: we'll calculate a team winning by taking the mode of all lane's predictions.

We transform our data:
```python
new_df = new_df.apply(lambda x: le.transform(x))

new_df.tail(5)
>	champ1	champ2
> 0	143	126
> 1	52	69
> 2	144	119
> 3	36	104
> 4	19	35
```
As we can see, our champion input variables have been properly one-hot encoded. As these are the two only variables we have for our model, applying a standard scaler will not make a difference, since all variables have a standard deviation of 1 between each other (all champions are translated into distinct integer numbers).

If we make the prediction:

```python
result = logreg.predict(new_df)

def find_winner(lst):
    return max(set(lst), key=lst.count)

winner_prediction = find_winner(result.tolist())
> [0 0 0 0 0]
```

The results for our prediction indicate the predicted winning team in each case. In this case, it's predicting champ2 to win in all five cases. This can be a coincidence or not, but it happens to be the correct prediction. In case of having discrepancies, we'd use the find_winner() function to find the mode of the prediction. Adding this to the ML model actually improves the implicit accuracy of our code, but not of the model itself: we're simply combining a 51% accuracy ML model with additional statistics to make a better prediction. We may ask ourselves, how can we measure the accuracy of our combined ML-statistics model? The problem is **we can't**, since we have no programming framework able to assist us with this. We'd have to code our own object-oriented programming framework that extends the functionalities of the current pandas framework, for example. And the time required to do so greatly exceeds the expected results. It's better we focus our resources, as Data Scientists, in using the frameworks available to us with our structured data, and not reinventing the wheel; and finding a better model by improving the quality of our input data.

Finally, to see the results in a human-readable way, we need to apply the inverse_transform() function to our still-encoded data:

```python

inverse_prediction = new_df.apply(lambda x: le.inverse_transform(x)) # we apply inverse transform

if winner_prediction == 1:
    print('Predicted winner is team 1: \n{}'.format(str(inverse_prediction['champ1'])))
else:
     print('Predicted winner is team 2: \n{}'.format(str(inverse_prediction['champ2'])))

```
Now, we can see the following, with one prediction per case, totaling 5 cases, and one final team prediction, using our find_winner() function:

```
Predicted winner is team 2: 
Tristana
Lulu
Syndra
Sejuani
Gnar
```

## The Problem & Next Steps

In short, we haven't considered enough variables. The results of this ML model are no better than using simple statistics, and heavily relies on additional statistics' support to make a bit more sense. We need to expand our model further, which is what we'll do in our fourth article, coming shortly.

## How can I get started on OCI?

Remember you can always sign up for free to Oracle Cloud Infrastructure: we allow you to sign up for an Oracle Cloud account which provides a number of Always Free services and a Free Trial with US$300 of free credit to use on all eligible Oracle Cloud Infrastructure services for up to 30 days. The Always Free services are available for an **unlimited** period of time. The Free Trial services may be used until your US$300 of free credits are consumed or the 30 days has expired, whichever comes first. You can [sign up here for free](https://signup.cloud.oracle.com/).

## License

Written by [Ignacio Guillermo Martínez](https://www.linkedin.com/in/ignacio-g-martinez/) [@jasperan](https://github.com/jasperan)

Copyright (c) 2021 Oracle and/or its affiliates.