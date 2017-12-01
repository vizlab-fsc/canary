import os
import json
import boto3
import importlib.util
from moto import mock_sns, mock_sqs


def import_function(name):
    """import a lambda function's handler"""
    spec = importlib.util.spec_from_file_location(
        name, os.path.abspath('lambda/{}/service.py'.format(name)))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.handler


def create_topic(client, name):
    client.create_topic(Name=name)
    response = client.list_topics()
    return response['Topics'][-1]['TopicArn']


def create_queue(client, name):
    client.create_queue(QueueName=name)
    queue_url = client.get_queue_url(QueueName=name)['QueueUrl']
    queue_attrs = client.get_queue_attributes(QueueUrl=queue_url,
                                                    AttributeNames=['All'])['Attributes']
    return queue_attrs['QueueArn'], queue_url


def get_messages(queue):
    messages = queue.receive_messages()
    return [json.loads(m.body) for m in messages]


def get_sns_events(queue):
    # <http://docs.aws.amazon.com/lambda/latest/dg/eventsources.html#eventsources-sns>
    return [{
        'Records': [{
            'Sns': message
        }]
    } for message in get_messages(queue)]


@mock_sns
@mock_sqs
def test():
    # load lambda functions
    handlers = {
        name: import_function(name)
        for name in ['arbiter', 'scraper', 'parser', 'downloader']
    }

    # setup mock messaging
    sns_client = boto3.client('sns')
    topics = {
        name: create_topic(sns_client, name)
        for name in ['arbiter', 'scraper', 'parser']
    }

    sqs_client = boto3.client('sqs')
    queue_arn, queue_url = create_queue(sqs_client, 'test-queue')

    sqs = boto3.resource('sqs')
    queue = sqs.Queue(queue_url)

    for name, arn in topics.items():
        sns_client.subscribe(
            TopicArn=arn,
            Protocol='sqs',
            Endpoint=queue_arn)

    print('arbiter')
    os.environ['sns_arn'] = topics['arbiter']
    handlers['arbiter']({}, {})
    events = get_sns_events(queue)
    queue.purge()

    for event in events:
        handlers['scraper'](event, {})

    events = get_sns_events(queue)
    print(events)
    queue.purge()


test()