# Creating the Model

## Recap and Introduction


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

![Breakdown of effort to train model](https://raw.githubusercontent.com/oracle-devrel/leagueoflegends-optimizer/blob/main/images/lab1-anaconda_1.PNG?raw=true)


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

## Loading Data

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

## Splitting into Train-Test


We split our data into train-test sets:

```python
# We want to predict the 'win' variable.
train_features = train_dataset.copy()
test_features = test_dataset.copy()

train_labels = train_features.pop('win') # returns column 'win'
test_labels = test_features.pop('win') # returns column 'win'
```

## Encoding Data

We encode the data following the Data Science process:

```python
le = LabelEncoder()

le = le.fit(champ_list) # fit the label encoder with the whole champion list.

train_features = train_features.apply(lambda x: le.transform(x))
test_features = test_features.apply(lambda x: le.transform(x))
```

Note that the `champ_list` referenced in this code block is the list of all unique champions in LoL.

## Normalizing/Scaling Data

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
# we create 5 different matchups, champ1[n] will play against champ2[n]
new_data = {
    'champ1': ['Xayah', 'Karma', 'Xerath', 'Gragas', 'Chogath'],
    'champ2': ['Tristana', 'Lulu', 'Syndra', 'Sejuani', 'Gnar']
}
new_df = pd.DataFrame(new_data)
```

In this case, as our model is very limited in regards to input variables, we make the following **assumption**: we'll calculate a team winning by taking the mode of all lanes' predictions.

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

As we can see, our champion input variables have been properly one-hot **encoded**. In this specific case, since these are the two only variables we have for our model, applying a standard scaler will not make a difference, because all variables have a standard deviation of 1 between each other (all champions are translated into distinct integer numbers).
> Note: in other cases, after applying one-hot encoding, it's also beneficial to apply normalization to the values, so that decision trees / ML models don't consider this variable to be more important than others with smaller values.

If we make the prediction:

```python
result = logreg.predict(new_df)

def find_winner(lst):
    return max(set(lst), key=lst.count)

winner_prediction = find_winner(result.tolist())
```

> [0 0 0 0 0]

The results of the prediction indicate the predicted winning team in each case. In this case, it's predicting `champ2` to win in all five cases. This can be a coincidence or not, but it happens to be the correct prediction. In case of having discrepancies, we'd use the `find_winner()` function created above to find the mode of the prediction. Adding this to the ML model actually improves the implicit accuracy of our code, but not of the model itself: we're simply combining a **51% accuracy** ML model with additional statistics to make a better prediction. 

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

