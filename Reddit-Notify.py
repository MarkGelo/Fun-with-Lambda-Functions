import json
import sys, os
# so all the dependencies are in the folder, if not here then cant, idk why, should learn
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'dependencies')))
import requests
import praw
import boto3
from botocore.exceptions import ClientError

# REDDIT API
USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']
CLIENTID = os.environ['CLIENTID']
CLIENTSECRET = os.environ['CLIENTSECRET']

reddit = praw.Reddit(user_agent="Comment Extraction (by /u/{})".format(USERNAME),
                     client_id=CLIENTID, client_secret=CLIENTSECRET,
                     username=USERNAME, password=PASSWORD)
                     
# SES -- email sending
SENDER = os.environ['SENDER']
RECIPIENT = os.environ['RECIPIENT']
AWS_REGION = 'us-east-1'
CHARSET = "UTF-8"

client = boto3.client('ses',region_name=AWS_REGION)

def get_comments(thread, upvotes, topic):
    # a VERY SIMPLE way of getting the comments
    # not all comments are parsed because a bunch of comments with low upvotes
    # reaches a point of diminishing returns
    # so limit = 10, is somewhat ok
    # should graph and see which limit is best tho
    # might also based on the amount of total comments on the post

    submission = reddit.submission(url = thread)
    global threadTitle
    threadTitle = submission.title
    submission.comments.replace_more(limit = 0) # expands the readmore, limit 10
    replies = []
    # iterates comment tree and stores bodies with scores greater than upvotes in arg
    comments = submission.comments.list()
    for comment in comments:
        if comment.score > upvotes:
            # only add if has '-' 'by' or top level comment (more likely to be a song cuz responding to thread)
            # pretty good imo
            if topic == 'Music':
                if comment.parent_id == comment.link_id or '-' in comment.body or 'by' in comment.body:
                    replies.append(comment.body.strip())
                    # print('{} --- {}'.format(comment.body, comment.score))
            else:
                replies.append(comment.body.strip())
    return replies

def search_oneDay(query):
    # gets top day submissions
    submissions = reddit.subreddit(query['subreddit']).top('day')
    passed = []
    # filter out those that doesnt satisfy the query
    for submission in submissions:
        if submission.score >= query['threadUpvotes'] and submission.num_comments >= query['threadComments']:
            for keyword in query['search']:
                if keyword.lower() in submission.title.lower():
                    url = 'https://www.reddit.com/r/{}/comments/{}'.format(submission.subreddit.display_name, submission.id)
                    passed.append([submission.title, submission.score, url])
    # get the comments of each of the threads that passed the query
    for thread in passed:
        comments = get_comments(thread[2], query['minUpvotes'], query['topic'])
        thread.append(comments)
    return passed

# parse comments as a body html
def parseComments(comments):
    newComments = [x.replace('\n', '<br>') for x in comments]
    body =  '''
    <p>{}<p>
            '''.format('<br>------------------------<br>'.join(newComments))
    return body

# make up the html file for the email
def parseAndSend(title, upvotes, url, comments, topic):
    subject = 'Reddit Notification - {}'.format(topic)
    
    body_text = (   'Reddit Notification'
                    'Check Reddit'
        )
    parsedComments = parseComments(comments)
    body_html =     '''
    <html>
    <header>
    <h1>{}</h1>
    <h2>Upvotes: {}</h2>
    <h2>URL: {}</h2>
    </header>
    <body{}</body>
    </html>
                    '''.format(title, upvotes, url, parsedComments)
    send(subject, body_html, body_text)

def send(subject, body_html, body_text):
    # try to send email
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=SENDER
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        
def lambda_handler(event, context):
    queries= [  {   'subreddit': 'worldnews+news', 'topic': 'Personal', #searches worldnews and news
                    'search': ['chicago', 'illinois', 'IIT', 'Illinois Institute of Technology'],
                    'threadUpvotes': 1000, 'threadComments': 200, 'minUpvotes': 150},
                {   'subreddit': 'AskReddit', 'topic': 'Music',
                    'search': ['song', 'songs', 'banger', 'music'],
                    'threadUpvotes': 2000, 'threadComments': 1000, 'minUpvotes': 250},
                {   'subreddit': 'Games+pcgaming', 'topic': 'Games', #searches through gaming subreddits
                    'search': ['GTA 6', 'GTA VI', 'Grand Theft Auto 6', 'Grand Theft Auto VI'],
                    'threadUpvotes': 1000, 'threadComments': 200, 'minUpvotes': 150}
                ]
    for query in queries:
        # search for submissions in the subreddit for the day matching the query
        threads = search_oneDay(query)
        # for each submission that matched, it will parse the submission and send an email with the info
        for thread in threads:
            parseAndSend(thread[0], thread[1], thread[2], thread[3], query['topic'])
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully searched through Reddit')
    }