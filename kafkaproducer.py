
""" To read the twitter stream and push it to Kafka """

import json
from kafka import SimpleProducer, KafkaClient
import tweepy
import ConfigParser

class TweeterStreamListener(tweepy.StreamListener):

    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()
        client = KafkaClient("localhost:9092")
        self.producer = SimpleProducer(client, async = True,
                          batch_send_every_n = 1000,
                          batch_send_every_t = 10)

    def on_data(self, data):
        try:
            temp={}
            decoded = json.loads(data)
            if decoded['coordinates']:
                #print "ID:%s Username:%s Tweet:%s"%(decoded['id'],decoded['user']['screen_name'],decoded['text'])
                temp["text"]= decoded['text']
                temp["id"]= str(decoded['id'])
                temp["name"]= decoded['user']['screen_name']
                temp["latitude"]= str(decoded['coordinates']['coordinates'][1])
                temp["longitude"]= str(decoded['coordinates']['coordinates'][0])
                final = json.dumps(temp)
                print final
                self.producer.send_messages(b'twitterstream', final)
        except Exception as e:
            print "***"+str(e)+"****"
        return True

    def on_error(self, status_code):
        print status_code
        print("Error received in kafka producer")
        return True

    def on_timeout(self):
        return True

if __name__ == '__main__':

    # Read the credententials from 'twitter-app-credentials.txt' file
    config = ConfigParser.ConfigParser()
    config.read('twitter-app-credentials.txt')

    consumerKey = config.get("DEFAULT","consumerKey")
    consumerSecret = config.get("DEFAULT","consumerSecret")
    accessToken = config.get("DEFAULT","accessToken")
    accessTokenSecret = config.get("DEFAULT","accessTokenSecret")

    # Create Auth object
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(auth)

    # Create stream and bind the listener to it
    stream = tweepy.Stream(auth, listener = TweeterStreamListener(api))
    stream.filter(track=['love','job','you','good','happy','hate','india'], languages = ['en'])
