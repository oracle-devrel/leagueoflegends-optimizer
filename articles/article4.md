# League of Legends Optimizer using Oracle Cloud Infrastructure: Real-Time predictions

## Recap and Introduction
Welcome to the fourth article of the League of Legends Optimizer series!

In this article, we'll look at how all the work we've done so far comes to fruition. In article 3, we developed several ML models with AutoML tools like AutoGluon. The first developed model didn't include too many variables, which caused very poor accuracy. After expanding the model further, we realized that including more variables increased the accuracy to a manageable ~83% accuracy with Neural Networks.

Also, it's worth mentioning that we didn't expand further on how to tap into live data from League of Legends. We're going to consider this as the main topic of this fourth article, by exploring Riot Game's **Live Client API**. It will allow us to access, through HTTP requests, real-time data while we're playing, in the hopes of being able to use the model developed in article 3 to make real-time predictions.

So, without further ado, let's back into it. Exciting times are coming if you keep reading!

## Riot Game's Live Client Data API

The Live Client Data API allows us to gather data during an active game. Many players don't know this, but whenever you play a LoL, port 2999, which is reserved for League, receives real-time data which we can easily access through HTTP requests.

There are several endpoints available, from which we're especially interested in the following:

```python
# GET https://127.0.0.1:2999/liveclientdata/allgamedata
# Sample output can be found in the following URL, if interested. https://static.developer.riotgames.com/docs/lol/liveclientdata_sample.json
# This endpoint encapsulates all other endpoints into one.
```

```python
# Get all data about the active player. (the one in localhost)
# GET ​https://127.0.0.1:2999/liveclientdata/activeplayer
{
    "abilities": {...},
    "championStats": {
      "abilityHaste": 0.00000000000000,
      "abilityPower": 0.00000000000000,
      "armor": 0.00000000000000,
      "armorPenetrationFlat": 0.0,
      "armorPenetrationPercent": 0.0,
      "attackDamage": 0.00000000000000,
      "attackRange": 0.0,
      "attackSpeed": 0.00000000000000,
      "bonusArmorPenetrationPercent": 0.0,
      "bonusMagicPenetrationPercent": 0.0,
      "cooldownReduction": 0.00,
      "critChance": 0.0,
      "critDamage": 0.0,
      "currentHealth": 0.0,
      "healthRegenRate": 0.00000000000000,
      "lifeSteal": 0.0,
      "magicLethality": 0.0,
      "magicPenetrationFlat": 0.0,
      "magicPenetrationPercent": 0.0,
      "magicResist": 0.00000000000000,
      "maxHealth": 0.00000000000000,
      "moveSpeed": 0.00000000000000,
      "physicalLethality": 0.0,
      "resourceMax": 0.00000000000000,
      "resourceRegenRate": 0.00000000000000,
      "resourceType": "MANA",
      "resourceValue": 0.00000000000000,
      "spellVamp": 0.0,
      "tenacity": 0.0
    }
    "currentGold": 0.0,
    "fullRunes": {...},
    "level": 1,
    "summonerName": "Riot Tuxedo"
}
```

```python
# Retrieve the list of heroes in the game and their stats.
# GET ​https://127.0.0.1:2999/liveclientdata/playerlist
[
    {
        "championName": "Annie",
        "isBot": false,
        "isDead": false,
        "items": [...],
        "level": 1,
        "position": "MIDDLE",
        "rawChampionName": "game_character_displayname_Annie",
        "respawnTimer": 0.0,
        "runes": {...},
        "scores": {...},
        "skinID": 0,
        "summonerName": "Riot Tuxedo",
        "summonerSpells": {...},
        "team": "ORDER"
    },
    ...
]
```

```python
# Retrieve the list of the current scores for the player.
# GET ​https://127.0.0.1:2999/liveclientdata/playerscores?summonerName=X
{
    "assists": 0,
    "creepScore": 0,
    "deaths": 0,
    "kills": 0,
    "wardScore": 0.0
}
```

We can access these endpoints through a web browser, or programatically. The only impediment is that the data can only be accessed through localhost (127.0.0.1) and requests coming in from a different IP address will be rejected automatically. So we'll need to consider this in our code.
From these endpoints, we are interested in extracting as much information as possible, cross-referencing the information we have in our already-trained model from article 3. Ideally, we want to be able to extract all variables  in article 3's model. For that, we'll explore the names of the variables we have and check them to see if there are equivalences.

Taking a look at the data available from the `allgamedata` endpoint, we can approach the problem in several ways: make a model based on KDA (kills / deaths / assists) or based on champion statistics. We'll go with the second option, as it's less straightforward to predict for a human than simply looking at the scoreboard (much easier for humans since that's what we're used to). So, we'll be operating with these variables:

```json
{
    "championStats": {
      "abilityHaste": 0.00000000000000,
      "abilityPower": 0.00000000000000,
      "armor": 0.00000000000000,
      "armorPenetrationFlat": 0.0,
      "armorPenetrationPercent": 0.0,
      "attackDamage": 0.00000000000000,
      "attackRange": 0.0,
      "attackSpeed": 0.00000000000000,
      "bonusArmorPenetrationPercent": 0.0,
      "bonusMagicPenetrationPercent": 0.0,
      "cooldownReduction": 0.00,
      "critChance": 0.0,
      "critDamage": 0.0,
      "currentHealth": 0.0,
      "healthRegenRate": 0.00000000000000,
      "lifeSteal": 0.0,
      "magicLethality": 0.0,
      "magicPenetrationFlat": 0.0,
      "magicPenetrationPercent": 0.0,
      "magicResist": 0.00000000000000,
      "maxHealth": 0.00000000000000,
      "moveSpeed": 0.00000000000000,
      "physicalLethality": 0.0,
      "resourceMax": 0.00000000000000,
      "resourceRegenRate": 0.00000000000000,
      "resourceType": "MANA",
      "resourceValue": 0.00000000000000,
      "spellVamp": 0.0,
      "tenacity": 0.0
}
```

From this example, anyone would probably say that these variables aren't enough to build a reliable model. But they're more than enough, as you'll discover through the rest of the article.

From a DB standpoint, we'll create a new JSON collection to create our training data: 

```python
# CLASSIFIER MODEL (LIVE CLIENT API AFFINITY DATA)
def process_predictor_liveclient(db):
	connection = db.get_connection()
	matches = connection.getSodaDatabase().createCollection('match_detail')
	print('Total match_detail documents (to process): {}'.format(matches.find().filter({'classifier_processed_liveclient': {"$ne":1}}).count()))
	
	for doc in matches.find().filter({'classifier_processed_liveclient': {"$ne":1}}).getCursor():
		content = doc.getContent()
		built_object = build_final_object_liveclient(content) # build data similar to the one given by the Live Client API from Riot.
		if built_object:
			for x in built_object:
				res = db.insert('predictor_liveclient', x) # insert in new collection.
				if res == -1:
					# Change column value to processed.
					print(doc.getContent().get('metadata').get('matchId'))
					change_column_value_by_key(db, 'match_detail', 'classifier_processed_liveclient', 1, doc.key) # after processing, update processed bit.
					break
	db.close_connection(connection)

# builds liveclient-affine data object.
def build_final_object_liveclient(json_object):
	all_frames = list()   
	match_id = str()
	try:
		match_id = json_object.get('metadata').get('matchId')
	except AttributeError:
		print('[DBG] ERR MATCH_ID RETRIEVAL: {}'.format(json_object))
		return

	winner = int()
	# Determine winner
	frames = json_object.get('info').get('frames')
	last_frame = frames[-1]
	last_event = last_frame.get('events')[-1]
	assert last_event.get('type') == 'GAME_END'
	winner = last_event.get('winningTeam')

	for x in json_object.get('info').get('frames'):

		for y in range(1, 11):
			frame = {
				"timestamp": x.get('timestamp')
			}
			frame['abilityPower'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('abilityPower')
			frame['armor'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('armor')
			frame['armorPenetrationFlat'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('armorPen')
			frame['armorPenetrationPercent'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('armorPenPercent')
			frame['attackDamage'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('attackDamage')
			frame['attackSpeed'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('attackSpeed')
			frame['bonusArmorPenetrationPercent'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('bonusArmorPenPercent')
			frame['bonusMagicPenetrationPercent'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('bonusMagicPenPercent')
			frame['cooldownReduction'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('cooldownReduction')
			frame['currentHealth'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('health')
			frame['maxHealth'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('healthMax')
			frame['healthRegenRate'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('healthRegen')
			frame['lifesteal'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('lifesteal')
			frame['magicPenetrationFlat'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('magicPen')
			frame['magicPenetrationPercent'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('magicPenPercent')
			frame['magicResist'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('magicResist')
			frame['moveSpeed'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('movementSpeed')
			frame['resourceValue'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('power')
			frame['resourceMax'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('powerMax')
			frame['resourceRegenRate'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('powerRegen')
			frame['spellVamp'] = x.get('participantFrames').get('{}'.format(y)).get('championStats').get('spellVamp')

			frame['identifier'] = '{}_{}'.format(match_id, x.get('participantFrames').get('{}'.format(y)).get('participantId'))

			if winner == 100:
				if y in (1,2,3,4,5):
					frame['winner'] = 1
				else:
					frame['winner'] = 0
			elif winner == 200:
				if y in (1,2,3,4,5):
					frame['winner'] = 0
				else:
					frame['winner'] = 1
			all_frames.append(frame)
			del frame
		
	return all_frames

```

With this structure, we're able to generate data which is exactly like the data provided by the Live Client Data API. Making this correspondence is important as it will allow us to compare real-time data with trained data. 

From the Live Client API standpoint, we have a similar structure, with some missing variables and different variable names. We can amend that by modifying the names of the variables from the Live Client Data API to match the names of our trained model; and by eliminating those variables from the original model that don't appear in the Live Client API:

```python
# This method parses input from Live Client API and adapts the names to what's expected in our ML model.
def process_and_predict(input):

    json_obj = json.loads(input)
    team_color = str()
    for x in json_obj['allPlayers']:
        if x['team'] == 'ORDER':
            team_color = 'blue'
        else:
            team_color = 'red'
        
        print('Team {}: {}'.format(team_color, x['championName']))

    # Timestamp given by the Live Client API is in thousands of a second from the starting point. (assumption)

    timestamp = int(json_obj['gameData']['gameTime'] * 1000)
    data = [
        json_obj['activePlayer']['championStats']['magicResist'],
        json_obj['activePlayer']['championStats']['healthRegenRate'],
        json_obj['activePlayer']['championStats']['spellVamp'],
        timestamp,
        json_obj['activePlayer']['championStats']['maxHealth'],
        json_obj['activePlayer']['championStats']['moveSpeed'],
        json_obj['activePlayer']['championStats']['attackDamage'],
        json_obj['activePlayer']['championStats']['armorPenetrationPercent'],
        json_obj['activePlayer']['championStats']['lifeSteal'],
        json_obj['activePlayer']['championStats']['abilityPower'],
        json_obj['activePlayer']['championStats']['resourceValue'],
        json_obj['activePlayer']['championStats']['magicPenetrationFlat'],
        json_obj['activePlayer']['championStats']['attackSpeed'],
        json_obj['activePlayer']['championStats']['currentHealth'],
        json_obj['activePlayer']['championStats']['armor'],
        json_obj['activePlayer']['championStats']['magicPenetrationPercent'],
        json_obj['activePlayer']['championStats']['resourceMax'],
        json_obj['activePlayer']['championStats']['resourceRegenRate']
    ]


    sample_df = pd.DataFrame([data], columns=['magicResist', 'healthRegenRate', 'spellVamp', 'timestamp', 'maxHealth',
        'moveSpeed', 'attackDamage', 'armorPenetrationPercent', 'lifesteal', 'abilityPower', 'resourceValue', 'magicPenetrationFlat',
        'attackSpeed', 'currentHealth', 'armor', 'magicPenetrationPercent', 'resourceMax', 'resourceRegenRate'])

    prediction = _PREDICTOR.predict(sample_df)
    pred_probs = _PREDICTOR.predict_proba(sample_df)

    expected_result = prediction.get(0)
    if expected_result == 0:
        print('Expected LOSS, {}% probable'.format(pred_probs.iloc[0][0] * 100))
    else:
        print('Expected WIN, {}% probable'.format(pred_probs.iloc[0][1] * 100))
    
    print('Win/loss probability: {}%/{}%'.format(
        pred_probs.iloc[0][1] * 100,
        pred_probs.iloc[0][0] * 100
    ))
```

Now that we have a plan, let's execute it step by step.

## Training the final classifier model

To achieve real-time predictions, we must first have a trained predictor. For that, we'll create an ML model that considers only the variables provided both in the Live Client Data API and in the offline API (articles 1 and 2). 
We get data from our Autonomous JSON DB. We'll consider 24 variables in total at the beginning.

```python
data = db.open_collection('predictor_liveclient')
all_data = list()
i = 0
for doc in data.find().getCursor():
    content = doc.getContent()
    all_data.append(content)
    i+= 1

print('Data length: {}'.format(len(all_data)))

# Data length: 3060133
```

We convert from non-relational to a relational structure, which is what ML models like!
```python
df = pd.read_json(json.dumps(all_data), orient='records')
```

Let's start our ML process with a sample 80%/20% train-test split and drop the columns we don't want (columns with constant values and player identifiers add no value).

```python
from autogluon.tabular import TabularPredictor, TabularDataset

df = TabularDataset(df)

# drop columns we don't want (constant values + identifier)
df = df.drop(columns=['bonusArmorPenetrationPercent', 'bonusMagicPenetrationPercent',
    'identifier', 'cooldownReduction', 'armorPenetrationFlat'])

train = df.sample(frac=0.8,random_state=200) #random state is a seed value
test = df.drop(train.index)
```

We specify that we want to predict the `winner` variable and perform the AutoML + hyperparametrization. Also, we export our model, as our plan is to use it in a Python script later on to make real-time predictions while we're playing.

```python
label = 'winner'

save_path = './autogluon_trained_models_liveclient_classifier'  # specifies folder to store trained models
predictor = TabularPredictor(label=label, path=save_path).fit(train)

y_test = test[label]  # values to predict
test_data_nolabel = test.drop(columns=[label]) 
test_data_nolabel.head(5)
```

| row | magicResist | healthRegenRate |	spellVamp |	timestamp |	maxHealth |	moveSpeed |	attackDamage |	armorPenetrationPercent |	lifesteal |	abilityPower |	resourceValue |	magicPenetrationFlat |	attackSpeed |	currentHealth |	armor |	magicPenetrationPercent |	resourceMax |	resourceRegenRate |
| :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | 
| 2 | 33 |	15 |	0 |	180067 |	698 |	345 |	77 |	0 |	0 |	0 |	30 |	0 |	118 |	644 |	41 |	0 |	125 |	0 |
| 4 | 30 |	18 |	0 |	180067 |	628 |	335 |	57 |	0 |	0 |	26 |	187 |	0 |	102 |	552 |	37 |	0 |	305 |	13 |
| 6 |	33 |	34 |	0 |	180067 |	710 |	340 |	62 |	0 |	0 |	15 |	251 |	0 |	114 |	503 |	42 |	0 |	383 |	149 |
| 7 |	29 |	19 |	0 |	180067 |	762 |	335 |	101 |	0 |	0 |	0 |	151 |	0 |	143 |	399 |	46 |	0 |	423 |	18 |
| 14 |	32 | 0 |	0 |	0 |	620 |	340 |	25 |	0 |	0 |	0 |	0 |	0 |	100 |	620 |	36 |	0 |	0 |	0 |

And we test our model.

```python
predictor = TabularPredictor.load(save_path)

y_pred = predictor.predict(test_data_nolabel)
print("Predictions: {}".format(y_pred))
```

Our most accurate models are:

```python
predictor.leaderboard(test, silent=False)
```

| id | model |	score_test |	score_val |	pred_time_test |	pred_time_val |	fit_time |	pred_time_test_marginal |	pred_time_val_marginal |	fit_time_marginal |	stack_level |	can_infer |	fit_order |
| :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: |
| 0 |	WeightedEnsemble_L2 |	0.66544 |	0.689078 |	12.998381 |	1.530008 |	866.161298 |	0.006004 |	0.006177 |	1.356416 |	2 |	True |	14 |
| 1 |	RandomForestGini |	0.66069 |	0.676831 |	2.016773 |	0.315675 |	22.368041 |	2.016773 |	0.315675 |	22.368041 |	1 |	True |	5 |
| 2 |	RandomForestEntr |	0.66011 |	0.677081 |	1.908432 |	0.314932 |	24.854358 |	1.908432 |	0.314932 |	24.854358 |	1 |	True |	6 |
| 3 |	ExtraTreesGini |	0.65994 |	0.669833 |	4.162963 |	0.314386 |	11.347579 |	4.162963 |	0.314386 |	11.347579 |	1 |	True |	8 |
| 4 |	ExtraTreesEntr |	0.65928 |	0.673332 |	3.386951 |	0.313787 |	11.595320 |	3.386951 |	0.313787 |	11.595320 |	1 |	True |	9 |
| 5 |	NeuralNetMXNet |	0.64286 |	0.648588 |	1.480003 |	0.242218 |	793.445433 |	1.480003 |	0.242218 |	793.445433 |	1 |	True |	12 |
| 6 |	LightGBMLarge |	0.60645 |	0.622844 |	0.079303 |	0.015620 |	3.809432 |	0.079303 |	0.015620 |	3.809432 |	1 |	True |	13 |
| 7 |	NeuralNetFastAI |	0.60542 |	0.615846 |	7.990198 |	0.051421 |	325.652130 |	7.990198 |	0.051421 |	325.652130 |	1 |	True |	10 |
| 8 |	XGBoost |	0.59687 |	0.614096 |	0.070154 |	0.033291 |	0.968276 |	0.070154 |	0.033291 |	0.968276 |	1 |	True |	11 |
| 9 |	LightGBM |	0.56626 |	0.575606 |	0.022063 |	0.011376 |	0.475452 |	0.022063 |	0.011376 |	0.475452 |	1 |	True |	4 |
| 10 |	LightGBMXT |	0.56100 |	0.572107 |	0.015192 |	0.011457 |	0.718697 |	0.015192 |	0.011457 |	0.718697 |	1 |	True |	3 |
| 11 |	CatBoost |	0.55881 |	0.565859 |	0.010589 |	0.009640 |	0.813448 |	0.010589 |	0.009640 |	0.813448 |	1 |	True |	7 |
| 12 |	KNeighborsUnif |	0.53039 |	0.534116 |	934.033610 |	40.197675 |	0.079255 |	934.033610 |	40.197675 |	0.079255 |	1 |	True |	1 |
| 13 |	KNeighborsDist |	0.53001 |	0.532617 |	955.057964 |	39.491652 |	0.077697 |	955.057964 |	39.491652 |	0.077697 |	1 |	True |	2 |


We see an average score of **66% categorization accuracy**. Note that this model has been trained with only 50 thousand rows, to drastically reduce the **pred_time_val** time (as our plan is to use the model in real time with the lowest latency possible). If we train the model with all rows (3 million+ in my dataset), we get about **83% accuracy**, but a much higher prediction time. 

And here are the feature importances:

```python
predictor.feature_importance(test)
```

| variable |	importance |	stddev |	p_value |	n |	p99_high |	p99_low |
| :--------: | :--------: | :--------: | :--------: | :--------: | :--------: | :--------: |
| timestamp |	0.115667 |	0.015044 |	0.002796 |	3 |	0.201873 |	0.029461 |
| attackDamage |	0.090333 |	0.018610 |	0.006927 |	3 |	0.196971 |	-0.016304 |
| abilityPower |	0.069000 |	0.009000 |	0.002812 |	3 |	0.120571 |	0.017429 |
| maxHealth |	0.044667 |	0.025541 |	0.046946 |	3 |	0.191018 |	-0.101685 |
| armor |	0.040667 |	0.021502 |	0.040951 |	3 |	0.163875 |	-0.082542 |
| resourceMax |	0.038667 |	0.009713 |	0.010195 |	3 |	0.094321 |	-0.016987 |
| magicResist |	0.037333 |	0.013650 |	0.020895 |	3 |	0.115552 |	-0.040885 |
| resourceValue |	0.030667 |	0.024028 |	0.078814 |	3 |	0.168348 |	-0.107015 |
| attackSpeed |	0.028667 |	0.022301 |	0.077944 |	3 |	0.156454 |	-0.099120 |
| resourceRegenRate |	0.027333 |	0.015503 |	0.046289 |	3 |	0.116165 |	-0.061499 |
| moveSpeed |	0.018333 |	0.017039 |	0.101700 |	3 |	0.115970 |	-0.079303 |
| currentHealth |	0.013000 |	0.012166 |	0.102702 |	3 |	0.082710 |	-0.056710 |
| healthRegenRate |	0.011333 |	0.013051 |	0.135733 |	3 |	0.086118 |	-0.063451 |
| lifesteal |	0.006667 |	0.009018 |	0.164422 |	3 |	0.058344 |	-0.045010 |
| armorPenetrationPercent |	0.006000 |	0.002000 |	0.017549 |	3 |	0.017460 |	-0.005460 |
| magicPenetrationFlat |	0.004333 |	0.003512 |	0.083025 |	3 |	0.024457 |	-0.015790 |
| magicPenetrationPercent |	0.002333 |	0.001528 |	0.059041 |	3 |	0.011086 |	-0.006420 |
| spellVamp |	-0.000667 |	0.000577 |	0.908248 |	3 |	0.002642 |	-0.003975 |

Note that, even if the timestamp can't be used to predict, it's still useful as a feature. This is because the rest of the data depends a lot on how long the League game has been in progress. So, in reality, this is a useful variable that complements the rest of the variables to determine whether a player's statistics are good or bad with respect to the game progress.

## Next Steps

Now that we have our model trained, we have the same data that the Live Client Data API. In the following article, we'll connect to the Live Client Data API and extract data from it with Python and make real-time predictions.

## How can I get started on OCI?

Remember that you can always sign up for free with OCI! Your Oracle Cloud account provides a number of Always Free services and a Free Trial with US$300 of free credit to use on all eligible OCI services for up to 30 days. These Always Free services are available for an **unlimited** period of time. The Free Trial services may be used until your US$300 of free credits are consumed or the 30 days has expired, whichever comes first. You can [sign up here for free](https://signup.cloud.oracle.com/?source=:ex:tb:::::WWMK211125P00027&SC=:ex:tb:::::WWMK211125P00027&pcode=WWMK211125P00027).

## Join the conversation!

If you’re curious about the goings-on of Oracle Developers in their natural habitat, come join us on our public Slack channel! We don’t mind being your fish bowl 🐠

## License

Written by [Ignacio Guillermo Martínez](https://www.linkedin.com/in/ignacio-g-martinez/) [@jasperan](https://github.com/jasperan), edited by [GreatGhostsss](https://github.com/GreatGhostsss)

Copyright (c) 2021 Oracle and/or its affiliates.

Licensed under the Universal Permissive License (UPL), Version 1.0.

See [LICENSE](../LICENSE) for more details.