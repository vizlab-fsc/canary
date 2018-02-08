import os
import json
import boto3
import logging
from lib.memory import prune
from lib.models import Source, Session
logger = logging.getLogger()

# TODO move this to env var?
# or just iterate over all sources in DB?
SOURCES = ['4chan:pol', '8chan:leftypol']


def handler(event, context):
    """
    (should run on a schedule)
    1. sends out sources for other functions to update
    """
    session = Session()
    client = boto3.client('sns')
    arn = os.environ['SNS_ARN']
    for name in SOURCES:
        logger.info(name)
        source = session.query(Source).filter(Source.name==name).first()
        site = source.api()
        thread_ids = site.get_thread_ids()
        for id in thread_ids:
            message = {
                'source': name,
                'source_id': source.id,
                'thread_id': id
            }
            client.publish(
                TopicArn=arn,
                Message=json.dumps({
                    'default': json.dumps(message)
                }),
                MessageStructure='json'
            )
        prune(name)
    session.close()
