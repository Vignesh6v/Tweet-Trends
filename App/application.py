from flask import Flask, request, jsonify, session, render_template,session
from datetime import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import ConfigParser
import logging

import json



application = Flask(__name__)
def __int__():
	pass

@application.route('/')
def index():
	logger= logging.getLogger('application')
	logger.setLevel(logging.INFO)
	fh = logging.FileHandler('spam.log')
	fh.setLevel(logging.INFO)
	logger.addHandler(fh)
	logger.info('content')
	return render_template('TweetMap.html', name="TweetMap")


@application.route('/subscrbe',methods=['POST'])
def load():
	logger= logging.getLogger('application')
	logger.setLevel(logging.INFO)
	fh = logging.FileHandler('printOutput.log')
	fh.setLevel(logging.INFO)
	config = ConfigParser.ConfigParser()
	config.read('aws-app-credentials.txt')
	accessToken = config.get("DEFAULT","accessToken")
	accessTokenSecret = config.get("DEFAULT","accessTokenSecret")
	try:
		messagetype=request.headers['x-amz-sns-message-type']
		if messagetype == "Notification":

			awsauth = AWS4Auth(accessToken, accessTokenSecret, "us-west-2", 'es')
			host = config.get("DEFAULT","host")
			es = Elasticsearch(
				hosts=[{'host': host, 'port': 443}],
				http_auth=awsauth,
				use_ssl=True,
				verify_certs=True,
				connection_class=RequestsHttpConnection
			)

			jsonString=str(request.data)
			logger.info(type(request.data))
			json1=json.loads(jsonString)
			logger.info(json1['Message'])
			message=json1['Message']
			messageDict=json.loads(message)
			logger.info(messageDict['id'])
			logger.info(message)
			res = es.index(index="twitter", doc_type='tweet', id=messageDict['id'], body=message)
			logger.info(res['created'])

		elif messagetype == "SubscriptionConfirmation":
			jsonString=str(request.data)
			logger.info (type(jsonString))
			json1=json.loads(jsonString)
			logger.info (json1['SubscribeURL'])

	except Exception as e:
		logger.info('Exception occurred - {}'.format(e))




@application.route('/search')
def search():
	config = ConfigParser.ConfigParser()
	config.read('aws-app-credentials.txt')
	accessToken = config.get("DEFAULT","accessToken")
	accessTokenSecret = config.get("DEFAULT","accessTokenSecret")
	search_key = request.args.get('search_key')
	search_key = search_key.lower()
	result_list = []
	awsauth = AWS4Auth(accessToken, accessTokenSecret, "us-west-2", 'es')
	host = config.get("DEFAULT","host")
	es = Elasticsearch(
		hosts=[{'host': host, 'port': 443}],
		http_auth=awsauth,
		use_ssl=True,
		verify_certs=True,
		connection_class=RequestsHttpConnection
	)
	res = es.search(index="twitter", body={"query": {"wildcard": {"text":'*'+search_key+'*'}}}, size=400)
	hits = res['hits']['hits']
	if hits:
		for hit in hits:
			latitude = hit['_source']['latitude']
			longitude = hit['_source']['longitude']
			sentiment_response = hit['_source']['sentiment']
			tweet_text = hit['_source']['text']
			result_list.append(dict(latitude=latitude, longitude=longitude, sentiment_response=sentiment_response, tweet_text=tweet_text))

	result_json = json.dumps(result_list)
	return result_json


if __name__ == '__main__':
	application.debug = True
	application.run()
