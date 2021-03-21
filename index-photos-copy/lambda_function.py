import json
import boto3
import datetime
import requests
import time

# Change before demo #
es_url = 'https://search-photos-bnrbmus63teifn3tn5obq24pjq.us-east-1.es.amazonaws.com'

def lambda_handler(event, context):

    rekognition = boto3.client('rekognition')
    s3 = boto3.client('s3')
    
    for rec in event['Records']:
        
        bucket = rec['s3']['bucket']['name']
        key = rec['s3']['object']['key']
        
        labels = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket':bucket,
                    'Name':key
                }
            },
            MaxLabels=10
        )    
        
        response = s3.head_object(
            Bucket=bucket,
            Key=key,
        )
        
        data = {
                "objectKey":key,
                "bucket":bucket,
                "createdTimestamp":datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "labels":[]
        }
        
        for label in labels['Labels']:
            data["labels"].append(label['Name'])
        
        if 'x-amz-meta-customlabels' in response['ResponseMetadata']['HTTPHeaders'].keys():
            user_labels = response['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customlabels']
            user_labels = [x.strip() for x in user_labels.split(',')]
            print('User added labels:', user_labels)
            for label in user_labels:
                data['labels'].append(label)
                
        req = requests.post(es_url + '/photos/_doc', 
                            auth = ('esmaster', 'Esmasterpass123!'),
                            data = json.dumps(data), 
                            headers = {"Content-Type": "application/json"})
                            
        print("- Added", key, "to S3 bucket", bucket, "and to ES.")
        print("- Labels:", data['labels'])
        
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps('index-photos Done.')
    }
