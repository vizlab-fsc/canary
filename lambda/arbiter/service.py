import os
import json
import boto3
import logging
from lib.memory import prune
from lib.models import Source, Session
from concurrent.futures import ThreadPoolExecutor
from functools import partial

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def process_source(client, arn, source):
    logger.info(source.name)
    site = source.api()
    thread_ids = site.get_thread_ids()
    for id in thread_ids:
        message = {
            'source': source.name,
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
    prune(source.name)
    return source


def handler(event, context):
    """
    (should run on a schedule)
    1. sends out sources for other functions to update
    """
    session = Session()
    client = boto3.client('sns')
    arn = os.environ['SNS_ARN']
    sources = session.query(Source).all()
    fn = partial(process_source, client, arn)
    with ThreadPoolExecutor(max_workers=10) as executor:
        for source in executor.map(fn, sources):
            logger.info('done: {}'.format(source.name))
    session.close()
