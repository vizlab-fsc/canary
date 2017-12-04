import os
import json
import boto3
from lib.util import parse_sns_event
from lib.models import Context, Session


def handler(event, context):
    """
    1. takes in a post
    2. saves new post to db
    3. sends image urls to other functions to process
    """
    session = Session()
    client = boto3.client('sns')
    arn = os.environ['sns_arn']

    event = parse_sns_event(event)
    post = event.get('post')
    source_id = event.get('source_id')
    images = post.pop('images')

    # check if post already is saved
    q = session.query(Context).filter(
        Context.lid==post['lid'],
        Context.source_id==source_id
    )
    exists = session.query(q.exists()).scalar()
    if not exists:
        context = Context(**post)
        session.add(context)
        session.commit()

        for img in images:
            # send out messages of post data for processing
            client.publish(
                TargetArn=arn,
                Message=json.dumps({
                    'context_id': context.id,
                    'url': img
                }),
                MessageStructure='json'
            )
    session.close()

    # TODO by this point posts are already recorded as seen
    # need some assurance that the post won't get lost b/w functions
    # this should probably send to a queue instead of directly invoking a lambda
    # function
