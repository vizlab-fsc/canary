import os
import json
import boto3
from lib.parser import image_urls
from lib.models import Context, Session


def handler(event, context):
    """
    1. takes in posts for a source
    2. extracts image urls
    3. saves new posts to db
    4. sends messages with the image urls for other
    functions to process
    """
    session = Session()
    client = boto3.client('sns')
    arn = os.environ['sns_arn']

    post = event.get('post')
    source_id = event.get('source_id')

    # get images, if any
    # if none, don't save the post
    images = post.pop('attachments')
    images.extend(image_urls(post))
    if not images:
        return

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
                    'default': json.dumps({
                        'context_id': context.id,
                        'url': img
                    })
                }),
                MessageStructure='json'
            )
    session.close()
