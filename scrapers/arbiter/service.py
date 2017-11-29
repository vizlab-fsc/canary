import os
import json
import boto3


def handler(event, context):
    client = boto3.client('sns')
    arn = os.environ['sns_arn']

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
