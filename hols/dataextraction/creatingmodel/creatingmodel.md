# Creating the Model

## Introduction
In this lab, we're creating a very primitive ML model. This model will use very few variables and will only have one target variable. It'll be useful to us as it introduces the most basic and fundamental ML concepts.

Estimated Lab Time: 45 minutes

### Prerequisites

* An Oracle Free Tier, Paid or LiveLabs Cloud Account
* Active Oracle Cloud Account with available credits to use for Data Science service.
* [Previously created](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/hols/dataextraction/infra/infra.md) OCI Data Science Environment

## Task 1: Downloading / Accessing Notebooks and Datasets

You can find everything covered here in two files:

1. (Recommended) If you're using the data found in the [Kaggle dataset](https://www.kaggle.com/jasperan/league-of-legends-1v1-matchups-results), go ahead and [**and download** this notebook](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/notebooks/hol1_offline_analysis.ipynb)
    - To download the notebook, click on __Raw__:

    ![](images/raw.jpg)

    - Then: 

    ![](images/savepage.jpg)

    - Finally, download [`1v1.csv`](https://www.kaggle.com/datasets/jasperan/league-of-legends-1v1-matchups-results?select=1v1.csv) and [`matchup.csv`](https://www.kaggle.com/datasets/jasperan/league-of-legends-1v1-matchups-results?select=matchups.csv) datasets from Kaggle:

    ![](images/downloadkaggle.jpg)

    > Note that the files you download directly from Kaggle, will most likely be in .zip format. You will have to **unzip** the files once you have them locally:

    ![](images/unzip.png)

2. (Optional) If you're using your own data (generating it by following the workshop), and you have [all the prerequisites](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/hols/dataextraction/intro/intro.md) installed, you can check out [this notebook](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/notebooks/hol1_online_analysis.ipynb) which connects directly to the Autonomous DB through Instant Client and the database's wallet and creates a model from scratch.

3. (Optional) For advanced users, if you have experience with the Kaggle API, you always have the possibility to download the dataset directly from Kaggle using [Kaggle's API](https://github.com/Kaggle/kaggle-api), and running this command in a terminal where `kaggle-cli` is installed:
    
    ```console
    kaggle datasets download jasperan/league-of-legends-1v1-matchups-results
    ```

## Task 2: Setting up OCI Data Science Environment

[Having previously created our OCI Data Science environment](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/hols/dataextraction/infra/infra.md), we need to install the necessary Python dependencies to execute our code. For that, we'll access our environment.

1. We open the notebook that was provisioned:

    ![](./images/select_data_science.jpg)

    > You may find the Data Science section by also searching in the top left bar, or in the Analytics & AI tab, if it doesn't appear in "Recently visited" for you:

    ![](images/analyticstab.png)

    Now, we have access to a [list of our Data Science projects launched within OCI.](https://cloud.oracle.com/data-science/projects) We access our project, and inside our project we'll find the notebook.

    > The name of the notebook may be different than shown here in the screenshot.

    ![](./images/open-notebook.png)

    ![](./images/open-notebook2.png)

    You should now see the Jupyter environment

    ![](./images/notebook.png)

2. We now need to load our notebook and datasets into our environment. For that, using the files from [the official repository](https://github.com/oracle-devrel/leagueoflegends-optimizer/tree/livelabs) locally, we use the upload button to transfer the files:

    ![](./images/upload.jpg)

    We need to upload the notebook called `hol1_offline_analysis.ipynb` (the one we downloaded in Task 1), and our datasets from Kaggle ([matchups.csv](https://www.kaggle.com/datasets/jasperan/league-of-legends-1v1-matchups-results?select=matchups.csv) and [1v1.csv](https://www.kaggle.com/datasets/jasperan/league-of-legends-1v1-matchups-results?select=1v1.csv)).

3. We run the first code cell in [the notebook](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/notebooks/hol1_offline_analysis.ipynb) to install the dependencies. In order to run the code cell, you can press the following button:

    ![](./images/firstcell.png)

    Or simply press SHIFT + Enter for running the selected cells. We should see the libraries / dependencies being installed:

    ![](./images/firstcell_after_execution.png)

4. Afterwards, we can run the rest of the notebook in sequence, in the same way as explained above.


## Task 3: The Data Structure

From the [Kaggle dataset](https://www.kaggle.com/jasperan/league-of-legends-1v1-matchups-results), we see an example of the data structure we're going to use to build our model:

![](./images/example_data_structure.png)


The intricacies of how we built the data structure and derived the result from it are explained in [a previous article](https://github.com/oracle-devrel/leagueoflegends-optimizer/blob/livelabs/articles/article2.md). It is important to remember that structuring and manipulating data in the data science process takes about 80 to 90% of the time, according to expert sources (image courtesy of [“2020 State of Data Science: Moving From Hype Toward Maturity.”](https://www.anaconda.com/state-of-data-science-2020)), and we shouldn't be discouraged when spending most of our time processing and manipulating data structures. The ML algorithm is the easy part if you've correctly identified the correct data structure and adapted it to the structure ML algorithms expect.

![Breakdown of effort to train model](../../../images/lab1-anaconda_1.png?raw=true)


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

> This code corresponds to cell #2 of the above mentioned notebook.

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

![](./images/matchups_head_1.png)


We see that the matchups.csv file contains information from every game, based on a `P_MATCH_ID`. In this case, we'll have the following ID structure:

![](./images/match_id_structure.png)

After exploring the dataset, we observe that, in order to create a meaningful model, and with the purpose of trying to make the model decide which champion should win in every matchup, we will modify this initial structure and adapt it to predict whether a champion won or not.

This assimilates the structure we want to have:

| match_id	| champ1 | champ2 |	win |
| :----------:	| :------:	| :------:	| :----: |
| `EUN1_2910807891_utility` |	Velkoz | Yuumi | 1 |
| `EUN1_2910807891_jungle` | Shaco |	Nidalee	| 1 |
| `EUN1_2909987530_top` | Riven |	Sett |	0 |
| `EUN1_2909987530_middle` | Lissandra |	Kassadin |	0 |
| `EUN1_2909987530_bottom` | Ashe | Ezreal | 0 |


For this, we create a function that, for each `match_id`, finds whether the player won or not, and adds it as a boolean variable (True/False). It will also find the enemy player (in the same match and lane) and pair it against each other in the same row.

Therefore, we'll have one row per lane, per match.

> Note: the below code and processing must only be done if working with [the online analysis notebook](../../../notebooks/hol1_online_analysis.ipynb), since [the offline analysis notebook](../../../notebooks/hol1_offline_analysis.ipynb) already has this processing implemented into the original dataset.

```python
# OPTIONAL code: only execute if using your own data with the online analysis notebook.
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



After creating this function and invoking it, we will obtain a resulting CSV file or dataframe object. We'll use this new object to create our model.

## Task 5: Loading Processed Dataset

After doing this initial processing and understanding why variables are included, we load the new CSV file:


![](./images/1v1_output.png)

## Task 6: Exploring Data

We can check the list of champions in the game:

![](./images/champ_list_output.png)


> The result is exactly name if we run df['champ2'].unique(), as we have enough rows that cause all champions in the game to appear in both __champ1__ and __champ2__ columns.

> (Optional) It could be interesting to make an analysis of this data to see which champions were played the most, depending on the patch number (column __GAMEVERSION__).

To make sure we have all desired columns in our dataset, we print the columns:

![](./images/columns_output.png)


Finally, we print information about the dataset, to check whether we have any null / empty values in any of the columns:

![](./images/info_output.png)


In this case we don't have any null-values, otherwise we'd drop these null values or replace them with filler values / placeholders. This is especially important to check if the dataset hasn't been curated by anyone else before; checking for **data consistency** is very important if the dataset is produced by ourselves.

## Task 7: Dropping ID columns

![](./images/task7.png)


> Note: the inplace=True option persists the __drop__ operation in the __df__ object. This basically means that we don't need to assign this operation back to the dataframe, as the operation is performed directly on the same dataframe.

## Task 8: Splitting into Train-Test

To perform ML properly, we need to take the dataset we're going to work with, and split it into two:

- A training dataset, from which our ML model will learn to make predictions.
- A testing dataset, from which our ML model will validate the predictions it makes, and check how accurate it was compared to the truth.

In ML, it's very typical to find a 80% train / 20% test structure, as it provides enough data for the model to be trained, and enough data to check the accuracy of the model without having too much / too little data in either of the datasets.


We split our data into train-test sets:

![](./images/task8.png)

## Task 9: Encoding Data

In order for an ML model to accept "words", or as we call them, "Strings" or categorical variables, we need to make a conversion from a String into a meaningful thing for the model. We have to understand that a ML model is just a result of a computer making millions of operations per second; and all these operations are made with numbers.

Therefore, we'll always need to modify our String columns into numerical columns in one way or the other. There are mainly **two** ways to do this:

- Label encoding: each distinct String / word will be represented by a distinct number.
    > So, imagine we have 5 different Strings, we'll end up with an encoded column with values in the range of [0, 4].
- One-Hot encoding: this technique creates additional features / columns, based on the number of unique values in the column we're trying to convert. In computer terms, it performs a "binary representation" of any String.
    > So, for the previous example where we have 5 different Strings, we'd end up with 3 additional columns (2^2=4 (not enough), 2^3=8 (enough)), and every String would be represented in its binary form. E.g. String 1 would be 000 (0 in decimal), the last String would be 101 (4 in decimal).

One-hot encoding is typically more complex and requires some knowledge about binary calculus, if you want to fully understand it. It's much easier to use **label encoding**. 


So, that's what we do here. We encode the data following the Data Science process:

![](./images/task9.png)

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

![](./images/task10_1.png)

After scaling the data, we can fit our model. We choose a Logistic Regression model as an example:

![](./images/task10_2.png)

> Note: find additional documentation on [available sklearn linear models here.](https://scikit-learn.org/stable/modules/linear_model.html)

The accuracies obtained for the logistic regression classifier are 0.51. With so few variables, this is expected. We could be making better assumptions by having a bit of knowledge about the game and champion performances. We need to improve our model in some way. There are different ways to do this:

- Adding meaningful variables to the model
- Testing new regression / classification algorithms, other than Logistic Regression
- Having a more specific target variable. This target variable is only a boolean and doesn't allow for fine-grained predictions, it's either 0 or 1.

## Task 11: Making New Predictions

However, we can still make predictions using our model. The code to make a prediction needs to consider new data, encode it and then make a prediction.

First:

![](./images/task11_1.png)


Now, we transform our data.

![](./images/task11_2.png)


> Note: the data we create, we also have to apply the same transformations as we did to the original model, otherwise the model wouldn't understand the input!

And we get our label-encoded columns:

![](./images/task11_3.png)


As we can see, our champion input variables have been properly label-**encoded**. In this specific case, since these are the two only variables we have for our model (feature variables, variables we use to predict), applying a standard scaler will not make a difference, because all variables have a standard deviation of 1 between each other (all champions are translated into distinct integer numbers).
> Note: in other cases, after applying label encoding, it's also beneficial to scale values, so that decision trees / ML models don't consider this variable to be more important than others with smaller values.

In our model, as it is very __limited__ in regards to input variables and accuracy, we'll make assumptions / calculations of our own: we'll calculate a team's winning chances by calculating the winning probability of each lane, and seeing how much these probabilities differ.


If we make the prediction:

![](./images/task11_4.png)

Finally, we create an auxiliary function to tell us which team is more likely to win. We calculate any probability that exceeds 50% and sum them all.

![](./images/task11_5.png)


The results of the prediction indicates the predicted winning team in each case. In this case, it's predicting `champ1` to win in three out of five. Adding this to the ML model actually improves the conclusions we can extract from our model, but not of the model itself: we're simply combining a **51% accuracy** ML model with additional statistics to attempt a better prediction. 

Finally, to see the results in a human-readable way, we need to apply the `inverse_transform()` function to our still-encoded data:

![](./images/task11_6.png)

We can see which champions are from each team, and return human-readable results, which makes our model more understandable.

You may now [proceed to the next lab](#next).


## Acknowledgements

* **Author** - Nacho Martinez, Data Science Advocate @ DevRel
* **Contributors** -  Victor Martin, Product Strategy Director
* **Last Updated By/Date** - August 16th, 2022
