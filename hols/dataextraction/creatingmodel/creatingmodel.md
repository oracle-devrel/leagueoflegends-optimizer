# Creating the Model


## Introduction
In this lab, we're going to create a very primitive ML model. This model will use very few variables and will only have one target variable. It'll be useful to us as it'll allow us to make an introduction towards the most basic and fundamental ML concepts.

Estimated Lab Time: xx minutes

### Prerequisites

* An Oracle Free Tier, Paid or LiveLabs Cloud Account
* Active Oracle Cloud Account with available credits to use for Data Science service.
* [Previously created](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/hols/dataextraction/infra/infra.md) OCI Data Science Environment

## Task 1: Downloading / Accessing Notebooks

Everything that we're going to talk about, you can find in two files:

1. (Recommended) If you're using the data found in the [Kaggle dataset](https://www.kaggle.com/jasperan/league-of-legends-1v1-matchups-results): [access this notebook](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/notebooks/hol1_offline_analysis.ipynb)

2. (Optional) If you're using your own data (generating it by following the workshop), and you have [all the prerequisites](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/hols/dataextraction/intro/intro.md) installed, you can check out [this notebook](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/notebooks/hol1_online_analysis.ipynb) that connects directly to the Autonomous DB through Instant Client and the database's wallet and creates a model from scratch.

3. (Optional) For advanced users, you always have the possibility to download the dataset directly from Kaggle using [Kaggle's API](https://github.com/Kaggle/kaggle-api), and running:
    
    ```console
    kaggle datasets download jasperan/league-of-legends-1v1-matchups-results
    ```

## Task 2: Setting up OCI Data Science Environment

[Having previously created our OCI Data Science environment](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/hols/dataextraction/infra/infra.md), we need to install the necessary Python dependencies to execute our code. For that, we'll access our environment.

1. We open the notebook that was provisioned:

    > The name of the notebook may be different than shown here in the screenshot.

    ![](./images/open-notebook.png)

    ![](./images/open-notebook2.png)

    You should now see the Jupyter environment

    ![](./images/notebook.png)

2. Now, we have to load our notebook and datasets into our environment. For that, having the files from [the official repository](https://github.com/oracle-devrel/leagueoflegends-optimizer/tree/livelabs) locally, we use the upload button to transfer the files:

    ![](./images/upload.jpg)

    We need to upload the notebook called [`hol1_offline_analysis.ipynb`](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/notebooks/hol1_offline_analysis.ipynb), and our datasets from Kaggle ([matchups.csv](https://www.kaggle.com/datasets/jasperan/league-of-legends-1v1-matchups-results?select=matchups.csv) and [1v1.csv](https://www.kaggle.com/datasets/jasperan/league-of-legends-1v1-matchups-results?select=1v1.csv)).

3. We run the first code cell in [the notebook we will access]((https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/notebooks/hol1_offline_analysis.ipynb) to install the dependencies.

4. Afterwards, we can run the rest of the notebook in sequence.


## Task 3: The Data Structure

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

The intricacies of how we built the data structure and derived the result from it are explained in [a previous article](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/articles/article2.md). It is important to remember that structuring and manipulating data in the data science process takes about 80 to 90% of the time, according to expert sources (image courtesy of [“2020 State of Data Science: Moving From Hype Toward Maturity.”](https://www.anaconda.com/state-of-data-science-2020)), and we shouldn't be discouraged when spending most of our time processing and manipulating data structures. The ML algorithm is the easy part if you've correctly identified the correct data structure and adapted it to the structure ML algorithms expect.

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

## Task 4: Loading Data / Generating Dataset

We begin with simple data exploration of our initial dataset.

```python
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import json
import os
pd.set_option('float_format', '{:f}'.format)

import seaborn as sns
import matplotlib.pyplot as plt
%matplotlib inline

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler 
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# We read the dataset from the local file
df = pd.read_csv('matchups.csv', sep=',')
df.head(5)
```

| `P_MATCH_ID` | GOLDEARNED |	TOTALMINIONSKILLED |	WIN |	KILLS |	ASSISTS |	DEATHS |	CHAMPION |	VISIONSCORE |	PUUID |	TOTALDAMAGEDEALTTOCHAMPIONS |	SUMMONERNAME |	GAMEVERSION |
| :----------:	| :------:	| :------:	| :----: | :----------:	| :------:	| :------:	| :----: | :----------:	| :------:	| :------:	| :----: | :----------:	|
| `BR1_2304032235_utility` |	5218 |	16 |	False |	1 |	6 |	6 |	Bard |	28 |	`UNNl1KcPO98UoXiuRpQBefEKJbtCF_80b0_2s0Cwa5FiYia7CBuyoBqQwnvw6JDEIa8VDphv6wilow` |	4500 |	batata 12121212 |	11.13.382.1241 |
| `BR1_2304032235_utility` | 7515 |	29	|	True	| 1	| 20 |	1 |	Blitzcrank |	40 |	`w2DLeo91qdfD72dpGgapMOKh_4IZ9IMF29neabiS0QTe8WAzWX4UtexFXLSjfuasgyjH2wQgagVXwg` |	7716 |	love yourseIf |	11.13.382.1241 |	
| `BR1_2304032235_jungle` |	9197 |	47 |	False |	5 |	5 |	5 |	Nocturne |	17 |	`wDtmVguiopT93yrxtv2L88LxAVWC8E2fj_F3FDW81nCuSUffNCG0cQZJADKWx9GlJcQMuVWL_n9OBg` |	9696 |	NTM HACKER |	11.13.382.1241 |
| `BR1_2304032235_jungle` |	10564 |	37 |	True |	6 |	8 |	4 |	Kayn |	12 |	`zVKtTZrdKVIpXwIMlsuSQjwOgqxx0DMhnWDFL7MrAKxXZqZ8ksaJ9SVQ2Zjb-NrjQ4FB9LmDx-nx8w` |	15291 |	unsuri |	11.13.382.1241 |
| `BR1_2303451507_top` |	10598 |	158 |	False |	6 |	8 |	7 |	Pantheon |	17 |	`sTevUOXxKjNW7dpbtyu9wjn8KZxzN63_f2MfGc1EALDjtq7Z3JE0JZFvRtyuTjkGmbGPqMAEwvt0Hw` |	20568 |	Nome e Numeros |	11.13.382.1241 |
| `BR1_2303451507_top` |	13000 |	174 |	True |	10 |	4 |	6 |	Mordekaiser |	18 | `r7sMT1QKsGE_Y5O7o2tQMU8v6A5BA6hsyCKnvKqo7fAsxJ5_LXk4_7f2NW69uf5oR4YT9djAU88WKg` |	20672 |	Duianr |	11.13.382.1241 |

We see that the matchups.csv file contains information from every game, based on a `P_MATCH_ID`. In this case, we'll have the following ID structure:

```bash
XXn_YYYYYYYYY_z

where XX = region, YYYYYYYYY = match id, z = lane played in the match. Possible lanes are (utility, jungle, top, middle, bottom).
```

After exploring the dataset, we observe that, in order to create a meaningful model, and with the purpose of trying to make the model decide which champion should win in every matchup, we will modify this initial structure and adapt it to predict whether a champion won or not.

This assimilates the structure we want to have:

| match_id	| champ1 | champ2 |	win |
| :----------:	| :------:	| :------:	| :----: |
| `EUN1_2910807891_utility` |	Velkoz | Yuumi | 1 |
| `EUN1_2910807891_jungle` | Shaco |	Nidalee	| 1 |
| `EUN1_2909987530_top` | Riven |	Sett |	0 |
| `EUN1_2909987530_middle` | Lissandra |	Kassadin |	0 |
| `EUN1_2909987530_bottom` | Ashe | Ezreal | 0 |


For this, we create a function that, for each match_id, it finds whether the player won or not, and adds it as a boolean variable (True/False). It will also find the enemy player (in the same match and lane) and pair it against each other in the same row.

Therefore, we'll have one row per lane, per match.

```python
def process_1v1_model():
    # Now, set a processed_1v1 bit in the match
    collection_matchups = db.open_collection('matchups')
    collection_1v1_model = db.open_collection('1v1_model')
    matchup_documents = collection_matchups.find().getDocuments()

    for x in matchup_documents:
        #shuffled_list = random.shuffle(matchup_documents)
        match_id = x.getContent().get('p_match_id')
        data = x.getContent().get('data')
        champion_matchup = list()
        win_matchup = list()
        for y in data:
            champion_matchup.append(y.get('champion'))
            win_matchup.append(y.get('win'))
            win_var = int()
            if win_matchup[0] is True:
                win_var = 1
            else: 
                win_var = 0
        obj = {
            'match_id':match_id,
            'champ1':champion_matchup[0],
            'champ2':champion_matchup[1],
            'win': win_var
        }
        print(obj)
        try:
            db.insert('1v1_model', obj)
        except cx_Oracle.IntegrityError:
            continue
    print('Inserted {}'.format(obj))
```

> Note: this code and processing must only be done if working with [the online analysis notebook](../../../notebooks/hol1_online_analysis.ipynb), since [the offline analysis notebook](../../../notebooks/hol1_offline_analysis.ipynb) already has this processing implemented into the original dataset.

After creating this function and invoking it, we will obtain a resulting CSV file or dataframe object. We'll use this new object to create our model.

## Task 5: Loading Processed Dataset

After doing this initial processing and understanding why variables are included, we load the new CSV file:

```python
# We read the dataset from the local file, after taking a look at the original dataset.
df = pd.read_csv('1v1.csv', sep=',', engine='python')

df.head(5)
```

## Task 6: Exploring Data

We can check the list of champions in the game:

```python
champ_list = df['champ1'].unique().tolist()

print(type(champ_list), champ_list)
```


```bash
array(['Ezreal', 'Pyke', 'Diana', 'Jayce', 'Pantheon', 'Galio',
       'Mordekaiser', 'Anivia', 'Kalista', 'Brand', 'LeeSin', 'Katarina',
       'Jinx', 'Nami', 'Sylas', 'Irelia', 'Lucian', 'Zyra', 'Kayn', 'Zac',
       'Qiyana', 'Jhin', 'Caitlyn', 'Morgana', 'Viego', 'Tryndamere',
       'Kassadin', 'Camille', 'Leblanc', 'Draven', 'Syndra', 'Ziggs',
       'Bard', 'XinZhao', 'Nocturne', 'Yasuo', 'Riven', 'Corki', 'Karma',
       'Elise', 'MonkeyKing', 'Sivir', 'Blitzcrank', 'Jax', 'Zilean',
       'Ashe', 'Velkoz', 'DrMundo', 'Ekko', 'Thresh', 'Nunu', 'Sett',
       'Khazix', 'Cassiopeia', 'Kaisa', 'Nautilus', 'Gwen', 'Graves',
       'Volibear', 'KogMaw', 'Lulu', 'Ryze', 'Lux', 'Rengar', 'Alistar',
       'Karthus', 'Gragas', 'Shen', 'Neeko', 'TahmKench', 'Akali',
       'Vayne', 'Seraphine', 'Gnar', 'Tristana', 'Leona', 'Yone',
       'Viktor', 'Skarner', 'Garen', 'Zed', 'Soraka', 'Talon', 'Fiora',
       'TwistedFate', 'MissFortune', 'Veigar', 'Hecarim', 'Shyvana',
       'Aatrox', 'Sion', 'Kayle', 'Poppy', 'Rumble', 'Xerath', 'Orianna',
       'Janna', 'Renekton', 'Rakan', 'Maokai', 'MasterYi', 'AurelionSol',
       'Yuumi', 'Shaco', 'Lissandra', 'Zoe', 'Senna', 'Taliyah', 'Lillia',
       'Warwick', 'Varus', 'Darius', 'Udyr', 'Samira', 'Amumu',
       'Aphelios', 'Evelynn', 'Swain', 'Twitch', 'RekSai', 'Vi', 'Yorick',
       'Akshan', 'Vladimir', 'Malphite', 'FiddleSticks', 'Ornn',
       'Kindred', 'JarvanIV', 'Rell', 'Olaf', 'Urgot', 'Nidalee',
       'Heimerdinger', 'Ahri', 'Malzahar', 'Trundle', 'Gangplank',
       'Annie', 'Rammus', 'Xayah', 'Azir', 'Taric', 'Teemo', 'Sona',
       'Nasus', 'Kennen', 'Braum', 'Ivern', 'Chogath', 'Fizz', 'Quinn',
       'Kled', 'Singed', 'Sejuani', 'Illaoi'], dtype=object)
```

> The result is exactly name if we do df['champ2'].unique(), as we have enough rows that cause all champions in the game to appear in both __champ1__ and __champ2__ columns.
> (Optional) It could be interesting to make an analysis of this data to see which champions were played the most, depending on the patch number (column __GAMEVERSION__).

To make sure we have all desired columns in our dataset, we print the columns:

```python
print(df.columns) # we have 4 columns, 'win' is what we want to predict
```

```bash
> Index(['match_id', 'champ1', 'champ2', 'win'], dtype='object')
```


Finally, we print information about the dataset, to check whether we have any null / empty values in any of the columns:

```python
df.info()
```

```bash
> <class 'pandas.core.frame.DataFrame'>
RangeIndex: 1288773 entries, 0 to 1288772
Data columns (total 4 columns):
 #   Column    Non-Null Count    Dtype 
---  ------    --------------    ----- 
 0   match_id  1288773 non-null  int64 
 1   champ1    1288773 non-null  object
 2   champ2    1288773 non-null  object
 3   win       1288773 non-null  int64 
dtypes: int64(2), object(2)
memory usage: 39.3+ MB
```

In this case we don't have any null-values, otherwise we'd drop these null values or replace them with filler values / placeholders. This is especially important to check if the dataset hasn't been curated by anyone else before; checking for **data consistency** is very important if the dataset is produced by ourselves.

## Task 7: Dropping ID columns

```python
# Drop match_id column as it's a String that provides no value towards predictions, almost every value is different, and all values are categorical (Strings), not numbers.
df.drop(['match_id'], axis=1, inplace=True)
```

> Note: the inplace=True option persists the __drop__ operation in the __df__ object. This basically means that we don't need to assign this operation back to the dataframe, as the operation is performed directly on the same dataframe.

## Task 8: Splitting into Train-Test

To perform ML properly, we need to take the dataset we're going to work with, and split it into two:
- A training dataset, from which our ML model will learn to make predictions.
- A testing dataset, from which our ML model will validate the predictions it makes, and check how accurate it was compared to the truth.

In ML, it's very typical to find a 80% train / 20% test structure, as it provides enough data for the model to be trained, and enough data to check the accuracy of the model without having too much / too little data in either of the datasets.


We split our data into train-test sets:

```python
# Splitting features (what we use to predict) from labels (what we want to predict)
# We want to predict the 'win' variable.
# The rest of variables will be inputs.

train_features = train_dataset.copy()
test_features = test_dataset.copy()

train_labels = train_features.pop('win') # returns column 'win'
test_labels = test_features.pop('win') # returns column 'win'
```

## Task 9: Encoding Data

In order for a ML model to accept "words", or as we call them, "Strings" or categorical variables, we need to make a conversion from a String into a meaningful thing for the model. We have to understand that a ML model is just a result of a computer making millions of operations per second; and all these operations are made with numbers.

Therefore, we'll always need to modify our String columns into numerical columns in one way or the other. There are mainly **two** ways to do this:
- Label encoding: each distinct String / word will be represented by a distinct number.
    > So, imagine we have 5 different Strings, we'll end up with an encoded column with values in the range of [0, 4].
- One-Hot encoding: this technique creates additional features / columns, based on the number of unique values in the column we're trying to convert. In computer terms, it performs a "binary representation" of any String.
    > So, for the previous example where we have 5 different Strings, we'd end up with 3 additional columns (2^2=4 (not enough), 2^3=8 (enough)), and every String would be represented in its binary form. E.g. String 1 would be 000 (0 in decimal), the last String would be 101 (4 in decimal).

One-hot encoding is typically more complex and requires some knowledge about binary calculus, if you want to fully understand it. It's much easier to use **label encoding**. 


So, that's what we do here. We encode the data following the Data Science process:

```python
le = LabelEncoder() # we create our LabelEncoder object
le = le.fit(champ_list) # fit the label encoder with the whole champion list; meaning that it will consider as many
# values as distinct champions are in the champ_list list.

# we apply this transformation (found in the object 'le') to every row in the dataset
# through a lambda function. More info on lambda functions here: https://www.w3schools.com/python/python_lambda.asp
train_features = train_features.apply(lambda x: le.transform(x))
test_features = test_features.apply(lambda x: le.transform(x))
```

## Task 10: Scaling Data

Now that we have our categorical variables properly encoded into numerical variables, we need to apply **scaling** to all variables.
Why is this important? Because, depending on which ML model to train, each of them will behave differently; and some of these models may consider "bigger" values as more important; this isn't what we want.

Therefore, we need to scale all variables in these numerical columns, into variables with similar values, which ML models like more.

There are several ways to apply scaling:
- [Min/max scaling](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html): transforms a variable by scaling each value into a given range (modifiable, by default in the range [0, 1]).
- [Standard scaling](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html): it applies the following formula:
    z = (x - u) / s
    where z = scaled value, x = original value, u = feature mean/average, s = feature standard deviation


We'll apply standard scaling in this case, and apply the transformation to the datasets.
```python
# Scaling
scaler = StandardScaler()
train_features = scaler.fit_transform(train_features)
test_features = scaler.transform(test_features)
```

After scaling the data we can fit our model. We choose a Logistic Regression model as an example:

```python
from sklearn.linear_model import LogisticRegression

logreg = LogisticRegression()
logreg.fit(train_features, train_labels)
# score(X, y[, sample_weight]): Return the mean accuracy on the given test data and labels
print(logreg.predict_proba(train_features[:2, :]))
print(logreg.score(train_features, train_labels))
```
> Note: find additional documentation on [possible linear models from sklearn here.](https://scikit-learn.org/stable/modules/linear_model.html)

The accuracies obtained for the logistic regression classifier are 0.51. With so few variables, this is expected. We could be making better assumptions by having a bit of knowledge about the game and champion performances. We need to improve our model in some way. There are different ways to do this:
- Adding meaningful variables to the model
- Testing new regression / classification algorithms, other than Logistic Regression
- Having a more specific target variable. This target variable is only a boolean and doesn't allow for fine-grained predictions, it's either 0 or 1.

## Task 11: Making New Predictions

However, we can still make predictions using our model. The code to make a prediction needs to consider new data, encode it and then make a prediction.

First, 


```python
# we create 5 different matchups, champ1[n] will play against champ2[n]
new_data = {
    'champ1': ['Ezreal', 'Janna', 'Anivia', 'Gnar', 'Warwick'],
    'champ2': ['Jhin', 'Blitzcrank', 'Viktor', 'Jax', 'Amumu']

}
new_df = pd.DataFrame(new_data)

# we apply the transformations
new_df = new_df.apply(lambda x: le.transform(x)) # we use the previously created label encoder
scaled = scaler.fit_transform(new_df)

new_df.tail(5)
```

Let's transform our data.
> Note: the data we create, we also have to apply the same transformations as we did to the original model, otherwise the model wouldn't understand the input!

And we get our label-encoded columns:

| champ1 | champ2  |
| :---:	| :---:	|
| 143 | 126 |
| 52 | 69 |
| 144 | 119 |
| 36 | 104 |
| 19 | 35 |

As we can see, our champion input variables have been properly label-**encoded**. In this specific case, since these are the two only variables we have for our model (feature variables, variables we use to predict), applying a standard scaler will not make a difference, because all variables have a standard deviation of 1 between each other (all champions are translated into distinct integer numbers).
> Note: in other cases, after applying label encoding, it's also beneficial to scale values, so that decision trees / ML models don't consider this variable to be more important than others with smaller values.

In our model, as it is very __limited__ in regards to input variables and accuracy, we'll make assumptions / calculations of our own: we'll calculate a team's winning chances by calculating the winning probability of each lane, and seeing how much these probabilities differ.


If we make the prediction:

```python
detailed_result = logreg.predict_proba(new_df)
print(detailed_result)



def find_winner_new(lst):
    count_team_1 = 0; count_team_2 = 0
    count = 0
    extra_probabilities = list()
    for x in lst:
        print(x)
        additional_prob = (x[0] - 0.5) * 100
        extra_probabilities.append(additional_prob)
        if x[0] >= x[1]:
            #print('Champ 1 most likely to win ({}% additional probability)'.format(additional_prob))
            count_team_1 += 1
        else:
            #print('Champ 2 most likely to win ({}% additional probability)'.format((x[1]-x[0])*100))
            count_team_2 += 1
    return count_team_1, count_team_2, extra_probabilities


# we take the mode as a "normalizer"
team_1, team_2, probabilities = find_winner_new(detailed_result)
print(team_1, team_2, probabilities)

if team_1 > team_2:
    print('Team 1 most likely to win with an additional probability of {}'.format(sum(probabilities)))
else:
    print('Team 2 most likely to win with an additional probability of {}'.format(sum(probabilities)))
```

```bash
[0.57085824 0.42914176]
[0.496072 0.503928]
[0.73050918 0.26949082]
[0.56122379 0.43877621]
[0.3951099 0.6048901]
# predicted 3 winners for team 1, 2 winners for team 2 -> team 1 is decided to be the winner.
# then, we have the extra probability (from 50% onwards) that the prediction made by the model is accurate -> we can make calculations with these numbers as well.
3 2 [7.085823690873272, -0.3928003875371511, 23.05091752259806, 6.122379069905581, -10.489009544500005]
Team 1 most likely to win with an additional probability of 25.37731035133976
```

The results of the prediction indicate the predicted winning team in each case. In this case, it's predicting `champ1` to win in three out of five. Adding this to the ML model actually improves the conclusions we can extract from our model, but not of the model itself: we're simply combining a **51% accuracy** ML model with additional statistics to attempt a better prediction. 

Finally, to see the results in a human-readable way, we need to apply the `inverse_transform()` function to our still-encoded data:

```python
inverse_prediction = new_df.apply(lambda x: le.inverse_transform(x)) # we apply inverse transform

if result[0] == 1:
    print('Predicted winner is {}'.format(str(inverse_prediction['champ1'])))
else:
    print('Predicted winner is {}'.format(str(inverse_prediction['champ2'].to_string())))

```

```console
Predicted winner is 0          Jhin
1    Blitzcrank
2        Viktor
3           Jax
4         Amumu

```

## Conclusions

Congratulations, you have completed the Workshop! A recap of what we have learned is:
- How to provision resources in OCI for Data Science purposes
- How to create a datastore architecture for our problems
- How to data mine League of Legends through an API
- How to build and structure the data
- How to connect to the Live Client API
- How to load data, preprocess it, visualize the dataset
- How to create a model
- How to deploy this model, and make real-time predictions with it from new data

In the next workshop, we'll learn how to extend and improve the model significantly, where we'll go from having a 51% accuracy to about 83% accuracy after finalizing the whole process.

## Acknowledgements

* **Author** - Nacho Martinez, Data Science Advocate @ DevRel
* **Contributors** -  Victor Martin, Product Strategy Director
* **Last Updated By/Date** - July 21st, 2022
