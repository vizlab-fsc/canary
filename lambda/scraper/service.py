import os
import json
import boto3
from lib.util import parse_sns_event
from lib.domains import domain_for_name


def handler(event, context):
    """
    1. fetches recent posts for a source
    2. sends out each post to other functions
    """
    client = boto3.client('sns')
    arn = os.environ['sns_arn']

    event = parse_sns_event(event)
    source_id = event.get('source_id')

    site = domain_for_name(source_id)
    posts = site.get_posts()
    for post in posts:
        message = {
            'source_id': source_id,
            'post': post
        }
        client.publish(
            TargetArn=arn,
            Message=json.dumps({
                'default': json.dumps(message)
            }),
            MessageStructure='json'
        )
