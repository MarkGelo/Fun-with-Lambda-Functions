import requests
import tweepy
import boto3
import botocore
import os
import random
import json

consumer_key = os.environ['consumer_key']
consumer_secret = os.environ['consumer_secret']
access_token = os.environ['access_token']
access_secret = os.environ['access_secret']

s3 = boto3.resource('s3')
BUCKET_NAME = 'tomandjerryscreens'

# authenticate twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
twitterAPI = tweepy.API(auth)

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

    #tweet picture
    twitterAPI.update_with_media('/tmp/local.jpeg')

    # delete local image
    os.remove('/tmp/local.jpeg')
    
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully tweeted random frame')
    }