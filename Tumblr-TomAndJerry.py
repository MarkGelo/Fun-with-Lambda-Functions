import requests
import boto3
import botocore
import os
import random
import json
import pytumblr

consumer_key = os.environ['consumer_key']
consumer_secret = os.environ['consumer_secret']
oauth_token = os.environ['oauth_token']
oauth_secret = os.environ['oauth_secret']

s3 = boto3.resource('s3')
BUCKET_NAME = 'tomandjerryscreens'

# authenticate 
client = pytumblr.TumblrRestClient(
    consumer_key,
    consumer_secret,
    oauth_token,
    oauth_secret,
)

def lambda_handler(event, context):
    
    # list for file key
    keyArray = []
    # get random frame from bucket
    bucket = s3.Bucket(BUCKET_NAME)
    # 162 episodes, 1 - 162 prefix
    randomEpisode = random.randint(1, 162)
    # iterate over bucket with episode frames
    for frame in bucket.objects.filter(Prefix = '{}-'.format(randomEpisode)):
        # add keys of frames to keyArray
        keyArray.append('{}'.format(frame.key))
    
    # gets the amount of frames in the episode
    numFrames = len(keyArray)

    # get random frame
    randomFrame = random.randint(0, numFrames - 1)
    # think will reesult in error
    
    # get key for that frame
    KEY = keyArray[randomFrame]

    #download frame
    pic = s3.Bucket(BUCKET_NAME).download_file(KEY, '/tmp/local.jpeg')

    print(client.info)
    #post picture with tags
    client.create_photo(    'tomandjerryscreens', state = 'published',
                            tags = ['tom and jerry'],
                            data = '/tmp/local.jpeg')
    
    # delete local image
    os.remove('/tmp/local.jpeg')
    
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully posted random frame')
    }