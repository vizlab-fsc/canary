import os
import json
import boto3
from lib.util import parse_sns_event
from lib.domains import domain_for_name
from lib.parser import image_urls, is_image
from lib.memory import record_seen, filter_seen


def handler(event, context):
    """
    1. fetches recent posts for a source thread
    2. filters out posts that have already been seen
    3. extracts image urls & keeps only those with images
    4. sends out each post to other functions
    """
    # session = Session()
    client = boto3.client('sns')
    arn = os.environ['SNS_ARN']

    event = parse_sns_event(event)
    thread_id = event.get('thread_id')
    source_id = event.get('source_id')
    source = event.get('source')

    site = domain_for_name(source)
    posts = list(filter_seen(source, site.get_posts(thread_id)))
    for post in posts:
        # get images, if any
        # only pass along post if it has images
        images = [a for a in post.pop('attachments') if is_image(a)]
        images.extend(image_urls(post['content']))
        if not images:
            continue

        post['images'] = images
        client.publish(
            TopicArn=arn,
            Message=json.dumps({
                'default': json.dumps({
                    'source_id': source_id,
                    'post': post
                })
            }),
            MessageStructure='json'
        )
    # TODO if we're recording posts as seen here
    # need some assurance that the post won't get lost b/w functions
    # this should probably send to a queue instead of directly invoking a lambda
    # function
    record_seen(source, posts)
