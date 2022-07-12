# Introduction

Estimated Lab Time: xx minutes

In the previous related workshop, we've learned about:
- [x] Defined and modelled our problem, understanding the different steps in the drafting phase of the game
- [x] Explored the various endpoints offered by Riot Games in their official API
- [x] Pulled data from the most skilled players around the world and built a data set of these players, which left us with a structure like this in our non-relational autonomous database
- [x] Created data structures, such as the *matchup* structure, to represent the data we pulled from the API in an adversarial way: in this data structure (see [this dataset](https://www.kaggle.com/jasperan/league-of-legends-1v1-matchups-results)), we faced each lane in a game against the enemy's, and determined whether this player won or lost the game.

Following this data structure, we're going to make a reliable model that can predict the best champion to pick against another player using by using machine learning.


To create our first predictor and to test out the different possibilities of our models, we will build a structure that allows us to predict *individual* lane matchup results. This means, whatever happens in a match for every lane. Therefore, we will have 5 rows of data for each game that we process. The structure of a matchup is as follows, and is stored in our database automatically in the following way:


```json
{
    "p_match_id": "BR1_2133967391_jungle",
    "data": [
        {
            "goldEarned": 9414,
            "totalMinionsKilled": 62,
            "win": false,
            "kills": 1,
            "assists": 7,
            "deaths": 8,
            "champion": "Graves",
            "visionScore": 13,
            "puuid": "hRMN6-jyVZAm7nhzYioSiQxy4WfWqhaV7ozDjQZ9OMoE6HSv870_UAtVv6ybRilZGpIdzrz9VmqN-g",
            "totalDamageDealtToChampions": 12217,
            "summonerName": "divespeiro"
        },
        {
            "goldEarned": 10119,
            "totalMinionsKilled": 31,
            "win": true,
            "kills": 3,
            "assists": 10,
            "deaths": 3,
            "champion": "Diana",
            "visionScore": 22,
            "puuid": "UdbGG79WCOn0DkjLv1-dpBZaVxIf3Nt-p9_IdEz5RwCwmj-wOHXSPeserm4uJz5v-RUZnzgleUqgQg",
            "totalDamageDealtToChampions": 9178,
            "summonerName": "soza"
        }
    ],
    "gameVersion": "10.25.348.1797"
}
```

We've previously stored this information inside a new collection called *matchups*. It will only include two players (one from each enemy team), and the API explicitly allows us to check in which lane these players played in. For each game (excluding games with AFKs - Away From Keyboard, meaning players that never connected into the game) we will have five different matchups (toplane, midlane, jungle lane, physical damage lane and support lane). With this kind of structure, we will be able to check the best competitors for any lane and champion, which will help us make individual predictions and increase the chances of victory in the end.
> Note that the data available for one specific match will only be able to accurately predict results for a specific patch, since a champion may be optimal for patch 10.25 but really bad on the next one. That's why we also store the matchup game version in our collection structure, in case we'd like to make a model specific for a game patch at some point.

After considering this structure, we'll create **two** ML models:
1. **Offline Model**: this model will be able to make predictions based on historical data; it has no connection to the game when we play it. However, it will still be useful to help us in the champion selection / drafting process before joining games.
2. **Online Model**: this model will reproduce the data structure accessible from the Live Client API, and the idea is to connect the data streams when we're playing to our model, and return live predictions about how we're performing in the game.

Without further ado, let's get started.

### Prerequisites

* An Oracle Free Tier, Paid or LiveLabs Cloud Account
* Active Oracle Cloud Account with available credits to use for Data Science service.
* (Optional) Having completed [the first workshop](../../dataextraction/)

You may now [proceed to the next lab](#next).

## Acknowledgements

* **Author** - Nacho Martinez, Data Science Advocate @ DevRel
* **Contributors** -  Victor Martin, Product Strategy Director
* **Last Updated By/Date** - July 12th, 2022