import requests
import tweepy
import boto3
import botocore
import os
import random
import json
import pytumblr

# added tumblr and twitter in one script to get within the AWS S3 free limit
# now, the same images will be uploaded to twitter and tumblr at the same time

# twitter
consumer_key = os.environ['consumer_key']
consumer_secret = os.environ['consumer_secret']
access_token = os.environ['access_token']
access_secret = os.environ['access_secret']

# tumblr
tumblr_consumer_key = os.environ['tumblr_consumer_key']
tumblr_consumer_secret = os.environ['tumblr_consumer_secret']
tumblr_oauth_token = os.environ['tumblr_oauth_token']
tumblr_oauth_secret = os.environ['tumblr_oauth_secret']

s3 = boto3.resource('s3')
BUCKET_NAME = 'tomandjerryscreens'

# authenticate twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
twitterAPI = tweepy.API(auth)

# authenticate tumblr
tumblr_client = pytumblr.TumblrRestClient(
    tumblr_consumer_key,
    tumblr_consumer_secret,
    tumblr_oauth_token,
    tumblr_oauth_secret,
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
    
    # get key for that frame
    KEY = keyArray[randomFrame]

    # download frame
    pic = s3.Bucket(BUCKET_NAME).download_file(KEY, '/tmp/local.jpeg')

    # tweet picture
    twitterAPI.update_with_media('/tmp/local.jpeg')

    # post picture to tumblr
    tumblr_client.create_photo('tomandjerryscreens', state = 'published',
                            tags = ['tom and jerry'],
                            data = '/tmp/local.jpeg')

    # delete local image
    os.remove('/tmp/local.jpeg')
    
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully tweeted and posted random frame to twitter and tumblr')
    }
