import os
import json
import boto3
from lib.domains import chan


def handler(event, context):
    client = boto3.client('sns')
    arn = os.environ['sns_arn']

    # TODO might be better not to hardcode these
    sites = [chan.FourChan('pol')]
    for site in sites:
        # TODO should we have some way of
        # identifying threads we've already seen
        # so we only update them, rather than
        # fetch the whole thing?
        seen = {}
        site.threads_to_update(seen)

    # TODO
    # this should poll each target site
    # and generate messages for the `scraper` functions.
    message = {'id': 1, 'domain': 'chan:pol'}

    response = client.publish(
        TargetArn=arn,
        Message=json.dumps({
            'default': json.dumps(message)
        }),
        MessageStructure='json'
    )
    return response
