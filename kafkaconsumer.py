
""" To read from kafkacluster and send to aws sns"""
from kafka import KafkaConsumer
from alchemyapi import AlchemyAPI
import json
import ConfigParser
import boto3

KAFKA_HOST = 'localhost:9092'
TOPIC = 'twitterstream'
TIMEOUT = 10000


def main():
    config = ConfigParser.ConfigParser()
    config.read('aws-app-credentials.txt')
    #sns access
    sns = boto3.client(
        'sns',
        aws_access_key_id= config.get("DEFAULT","accessToken"),
        aws_secret_access_key= config.get("DEFAULT","accessTokenSecret")
    )
    mytopic_arn = config.get("DEFAULT","TopicArn")
    # KafkaConsumer Object
    consumer = KafkaConsumer(TOPIC, bootstrap_servers=[KAFKA_HOST],
                             consumer_timeout_ms=-1)

    # read messages and get sentiment for the tweet text
    for message in consumer:
        tweetContent = json.loads(message.value)
        try:
            sentinmentText = tweetContent['text']
            response = AlchemyAPI().sentiment("text",sentinmentText)
            print response
            tweetContent['sentiment'] = response["docSentiment"]["type"]
            print "Sentiment: ", response["docSentiment"]["type"]
            print "Received tweet:", tweetContent['text']

            # publish to sns

            json_message = json.dumps({"default":json.dumps(tweetContent)})
            print "message: %s type: %s"%(json_message,type(json_message))
            sns.publish(TopicArn=mytopic_arn,Subject="Tweet",MessageStructure="json",Message=json_message)
        except Exception as e:
            print e
            print '*******'


if __name__ == '__main__':
    main()
