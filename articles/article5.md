## Connecting to the Live Client Data API

https://developer.riotgames.com/docs/lol

https://static.developer.riotgames.com/img/docs/lol/lcu_architecture.png

In an article on the Riot Games Engineering Blog, there's an image that is useful for defining what we're classifying as "League Client APIs".

Specifically, we're referring to a set of protocols that the Chromium Embedded Framework (CEF) uses to communicate with a C++ Library that in turn communicates with the League of Legends platform. As you'll notice, the communications between the C++ library and the CEF all occur locally on your desktop. This is the League Client API. This service is not officially supported for use with third party applications.

NOTE: We provide no guarantees of full documentation, service uptime, or change communication for unsupported services. This team does not own any components of the underlying services, and will not offer additional support related to them.

What's next

Whether you're combining the Riot Games API and League Client API, or doing something by only using the League Client endpoints, we need to know about it. Either create a new application or leave a note on your existing application in the Developer Portal. We need to know which endpoints you're using and how you're using them in order to expand on current or future feature sets. If you have any questions please join the Developer Discord for help.

Live Client Data API

The Live Client Data API provides a method for gathering data during an active game. It includes general information about the game as well player data.
Get All Game Data

The Live Client Data API has a number of endpoints that return a subset of the data returned by the /allgamedata endpoint. This endpoint is great for testing the Live Client Data API, but unless you actually need all the data from this endpoint, we suggest one of the endpoints listed below that return a subset of the response. 

