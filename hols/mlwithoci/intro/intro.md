# Introduction

Estimated Lab Time: xx minutes

In the previous related workshop, we've learned about:
- [x] Defined and modelled our problem, understanding the different steps in the drafting phase of the game
- [x] Explored the various endpoints offered by Riot Games in their official API
- [x] Pulled data from the most skilled players around the world and built a data set of these players, which left us with a structure like this in our non-relational autonomous database
- [x] Created data structures, such as the *matchup* structure, to represent the data we pulled from the API in an adversarial way: in this data structure (see [this dataset](https://www.kaggle.com/jasperan/league-of-legends-1v1-matchups-results)), we faced each lane in a game against the enemy's, and determined whether this player won or lost the game.
- [x] Created a simple ML model to explain basic concepts

With this workshop, we aim to improve our simple model in several ways to both improve the accuracy and the usability of the model.

After considering this structure, we can create **two** new ML models:

1. **Offline Model**: this model will be able to make predictions based on historical data; it has no connection to the game when we play it. However, it will still be useful to help us in the champion selection / drafting process before joining games. 
    > This model needs to have a greater accuracy than 51% (making random predictions).

2. **Online Model**: this model will reproduce the data structure accessible from the Live Client API, and the idea is to connect the data streams when we're playing to our model, and return live predictions about how we're performing in the game.

Let's get started.

### Prerequisites

* An Oracle Free Tier, Paid or LiveLabs Cloud Account
* Active Oracle Cloud Account with available credits to use for Data Science service.
* (Optional) Having completed [the first workshop](../../dataextraction/)

You may now [proceed to the next lab](#next).

## Acknowledgements

* **Author** - Nacho Martinez, Data Science Advocate @ DevRel
* **Contributors** -  Victor Martin, Product Strategy Director
* **Last Updated By/Date** - August 1st, 2022