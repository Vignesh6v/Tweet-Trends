# Tweet-Trends
Leveraged tweet data using the twitter API and displayed the same on a HeatMap using the Google Maps API while utilizing the ElasticSearch changefeed property to stream live data for a particular keyword using kafka and sns, thus reducing the overhead of polling the database constantly for new tweet data.

* Used the Apache Kafka to create a processing queue for the Tweets that are delivered by the Twitter Streaming API.
* Used Amazon SNS service to update the status processing on each tweet so the UI can refresh.
* Integrated the third party cloud service API into the Tweet processing flow.

Overview:
=======

Streaming

* Reads a stream of tweets from the Twitter Streaming API.
* After fetching a new tweet, check to see if it has geolocation info and is in English.
* Once the tweet validates these filters, send a message to Kafka Cluster for asynchronous processing on the text of the tweet

Apache Kafka

* Defined a Kafka cluster that will pick up messages from the kafka producer to process. 
* Make a call to the sentiment API (Alchemy). This can return a positive, negative or neutral sentiment evaluation for the text of the submitted Tweet.
* As soon as the tweet is processed send a notification -using SNS- to an HTTP endpoint, that contains the information about the tweet.

Backend

* On receiving the notification, index this tweet in Elasticsearch and the sentiment of the tweet is preserved.
* The backend provides the functionality to the user to search for tweets that match a particular keyword. 

Frontend

* When a new tweet is indexed, visual indication on the frontend are provided. 
* The user can search the index via a dropdown.
* The tweets that match the query are plotted on the map using markers.

Architecture Diagram
=======

```bash
Note: Used Apache Kafka instead of AWS SQS
```
<img src = "https://github.com/Vignesh6v/Tweet-Trends/blob/master/static/ouIDUJT.png" align = "center">
