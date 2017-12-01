import os
import json
import boto3
from lib.models import Source, Session

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
    arn = os.environ['sns_arn']
    for name in SOURCES:
        source = session.query(Source).filter(Source.name==name).first()
        client.publish(
            TargetArn=arn,
            Message=json.dumps({
                'source_id': source.id
            }),
            MessageStructure='json'
        )
