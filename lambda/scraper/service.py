import os
import json
import boto3
from lib.util import parse_sns_event
from lib.domains import domain_for_name


def handler(event, context):
    """
    1. fetches recent posts for a source thread
    2. sends out each post to other functions
    """
    # session = Session()
    client = boto3.client('sns')
    arn = os.environ['sns_arn']

    event = parse_sns_event(event)
    thread_id = event.get('thread_id')
    source_id = event.get('source_id')
    source = event.get('source')

    site = domain_for_name(source)
    posts = site.get_posts(thread_id)
    for post in posts:
        client.publish(
            TargetArn=arn,
            Message=json.dumps({
                'source_id': source_id,
                'post': post
            }),
            MessageStructure='json'
        )
