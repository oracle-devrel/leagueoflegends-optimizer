# League of Legends Optimizer using Oracle Cloud Infrastructure: Real-Time predictions

## Recap and Introduction
Welcome to the fifth article of the League of Legends Optimizer series!

In this article, we'll test all the work that we've done in this article series. We'll see how these models that we've created make predictions that make sense. In short, we'll have a League of Legends companion in one of my games, and we'll be able to see how the model reflects the state of a game at any point, and is able to predict the outcome of the game (either a win or a loss). So, without further ado, let's get into it.

## Connecting to the Live Client Data API

To extract live game information, we need to access the Live Client Data API from Riot Games.

The League Client API involves a set of protocols that CEF (Chromium Embedded Framework) uses to communicate between the League of Legends process and a C++ library.

![](https://static.developer.riotgames.com/img/docs/lol/lcu_architecture.png?raw=true)

Communications between the CEF and this C++ library happen locally, that's why we're obligated to use localhost as our connection endpoint. You can find additional information about this communication [here.](https://developer.riotgames.com/docs/lol)

You can also refer back to article 4, where I explain the most interesting endpoints that we encounter when using the Live Client Data API. 

For this article, we'll use the following endpoint:

```python
# GET https://127.0.0.1:2999/liveclientdata/allgamedata
# Sample output can be found in the following URL, if interested. https://static.developer.riotgames.com/docs/lol/liveclientdata_sample.json
# This endpoint encapsulates all other endpoints into one.
```

When we join a League of Legends game, the League process opens port 2999. We'll use this to our advantage and we'll make recurring requests to localhost:2999 to extract live match information and incorporate it into our ML pipeline. The result from our ML model will tell us if we're likely to win or lose.

## Architecture

In order to make requests properly, we need to access localhost as the calling endpoint. However, we may not want to access data in a local computer where we are playing (as computer resources should be used to get maximum game performance). For that, I have created an architecture which uses **message queues** and would allow us to make requests from any machine in the Internet.

For this architecture proposal, I've created two files, which you can find in the [official repository for this article series](https://github.com/oracle-devrel/leagueoflegends-optimizer) under the src/ section: live_client_producer.py and live_client_receiver.py.

### Producer

The producer is in charge of making requests to localhost and storing them, without making any predictions itself. The idea behind this is to allow the computer where we're playing League to offload and concentrate on playing the match as well as possible, without adding extra complexity caused by making ML predictions (which can take quite a lot of resources).

Therefore, we declare the main part of our producer this way:

```python
while True:
    try:
        # We access the endpoint we mentioned above in the article
        response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
    except requests.exceptions.ConnectionError:
        # Try again every 5 seconds
        print('{} | Currently not in game'.format(datetime.datetime.now()))
        time.sleep(5)
        continue

    # Send to RabbitMQ queue.
    if response.status_code != 404:
        to_send = build_object(response.content)
        send_message('live_client', to_send)
    time.sleep(30) # wait 30 seconds before making another request
```

We need to consider that, if we're not inside a game, we'll get a ConnectionError exception. To avoid this hardware interrupt, we catch the exception and keep making requests to the endpoint until something useful comes in.

I've chosen **RabbitMQ message queues** a very simple and efficient solution to store our results into a queue. This ensures the following:
- Accessing and consuming the data present in the queues from any IP address, not only localhost
- Message order is guaranteed, should we ever need to make a time series visualization of our predictions.
Therefore, we declare our message queues. 

```python
_MQ_NAME = 'live_client'

credentials = PlainCredentials('league', 'league')
connection = pika.BlockingConnection(
pika.ConnectionParameters(
    '{}'.format(args.ip),
    5672,
    '/',
    credentials))

channel = connection.channel()
channel.queue_declare(queue=_MQ_NAME)
```

Note that, in the above code snippet, we need to create a __PlainCredentials__ object, otherwise authentication from a public network to our IP address where the producer is located would fail. [Check this article out](https://programmerall.com/article/92801023802/) to learn how to set up the virtual host, authentication and permissions for our newly-created user.

Additionally, every object that comes in needs to be processed and 'transformed' into the same structure expected by the ML pipeline:

```python
# We remove useless data like items (which also cause quotation marks issues in JSON deserialization)
def build_object(content):
    # We convert to JSON format
    content = response.json()
    for x in content['allPlayers']:
        del x['items'] # delete items to avoid quotation marks
    built_obj = {
        'activePlayer': content['activePlayer'],
        'allPlayers': content['allPlayers']
    }
    content = json.dumps(content)
    content = content.replace("'", "\"") # for security, but most times it's redundant.
    print(content)
    return content # content will be a string due to json.dumps()
```

And finally, we declare a function that takes the __message__ in string format, and inserts it into the message queue, ready to be consumed.

```python
def send_message(queue_name, message):
    channel.basic_publish(exchange='', routing_key=queue_name, body='{}'.format(message))
    print('{} | MQ {} OK'.format(datetime.datetime.now(), message))
```

As we've built our message queue producer, if we run this while in a game, our ever-growing message queue will store messages even if noone decides to "consume" them and make predictions. Now, we need to do exactly this through a **consumer**.

### Consumer

In the consumer, we'll connect to the RabbitMQ server (doesn't necessarily have to be located where we run our producer module, it can be anywhere as if it was an Apache web server, you just need to make sure connection in the producer and consumer both point to the same RabbitMQ server's IP address) and make predictions with the light model (trained with 50.000 rows from our original dataset, as using a bigger model would yield higher prediction times) we trained in article 4:

```python
# We load the AutoGluon model.
save_path = args.path  # specifies folder to store trained models
_PREDICTOR = TabularPredictor.load(save_path)

def main():
    try:
        # localhost if the rabbitmq server is located in the same machine as the receiver.
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=600, blocked_connection_timeout=300))
        channel = connection.channel()

        # declare queue, in case the receiver is initialized before the producer.
        channel.queue_declare(queue='live_client')

        def callback(ch, method, properties, body):
            print('{} | MQ Received packet'.format(datetime.datetime.now()))
            process_and_predict(body.decode())

        # consume queue
        channel.basic_consume(queue='live_client', on_message_callback=callback, auto_ack=True)
        
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming() # we listen 24/7 for new messages in the live_client queue
    except pika.exceptions.StreamLostError:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=600, blocked_connection_timeout=300))
```

Note: if you run into 'connection reset' error, [check out this documentation piece on pika](https://pika.readthedocs.io/en/stable/examples/heartbeat_and_blocked_timeouts.html) which adds some parameters to the pika ConnectionParameters object to ensure well-behaved connections.

And, every time we consume a message from the queue, we predict the outcome using our AutoGluon model, by calling **process_and_predict**:

```python
def process_and_predict(input):

    json_obj = json.loads(input)
    team_color = str()
    for x in json_obj['allPlayers']:
        if x['team'] == 'ORDER':
            team_color = 'blue'
        else:
            team_color = 'red'
        
        print('Team {}: {}'.format(team_color, x['championName']))

    # Timestamp given by the Live Client API is in thousands of a second from the starting point.

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

    # We build the structure as our ML pipeline expects it (column names, and order).
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

And that's the last code piece we need for everything to work. Now, we can get into a game and run our producer code (in the machine where we play the League match) and the consumer (simultaneously, although not necessary) to get real-time predictions on the game.

### The Game!

