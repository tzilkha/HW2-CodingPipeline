import json
import boto3
import datetime
import requests
import time

# Change before demo #
es_url = 'https://search-photos-bnrbmus63teifn3tn5obq24pjq.us-east-1.es.amazonaws.com'
s3_url = 'https://hw2-s3-bucket.s3.amazonaws.com/'

def lambda_handler(event, context):


    lex = boto3.client('lex-runtime')

    response = lex.post_text(
		botName = 'HWTwoLex',
		botAlias = 'dev',
		userId = "AUser",
		inputText = event['queryStringParameters']['q']
    )

    results = []
    
    if response["intentName"] != 'SearchIntent':
        print("- Could not extract with Lex.")
    else:
        for label in response['slots'].values():
            if label:
                print ('- Retrieving ES results for', label)
                
                res = requests.get(es_url + '/photos/_doc/_search?q='  + label , 
                                    auth = ('esmaster','Esmasterpass123!'),
                                    headers = {"Content-Type": "application/json"})
                for hit in res.json()['hits']['hits']:
                    results += [s3_url + hit['_source']['objectKey']]
    
    print(results)
    
    return {
        'statusCode': 200,
		'headers': {
			"Access-Control-Allow-Origin": "*",
			'Content-Type': 'application/json'
		},
        'body': json.dumps(results)
    }
