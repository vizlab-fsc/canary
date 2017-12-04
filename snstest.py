import os
import json
import time
import boto3
import importlib.util
import requests_cache
from tqdm import tqdm
from lib.memory import r
from lib.models import Session, Image, ImageUsage, Context
from moto import mock_sns, mock_sqs, mock_s3
from concurrent.futures import ThreadPoolExecutor


def parallel(fn, items, n_jobs=4):
    with ThreadPoolExecutor(max_workers=n_jobs) as executor:
        return [f for f in executor.map(fn, items)]


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
    queue_arn = queue_attrs['QueueArn']
    return queue_url, queue_arn



def get_messages(queue):
    """consume all available messages from the queue.
    we can only get 10 at a time."""
    msgs = None
    while msgs is None or msgs:
        msgs = queue.receive_messages(MaxNumberOfMessages=10)
        receipts = [{
            'Id': m.message_id,
            'ReceiptHandle': m.receipt_handle
        } for m in msgs]
        yield [sqs_as_sns(json.loads(m.body)) for m in msgs], receipts


def process_queue(handler, queue):
    runtimes = []
    n_messages = int(queue.attributes['ApproximateNumberOfMessages'])
    print('messages:', n_messages)
    with tqdm(total=n_messages) as pbar:
        for events, receipts in get_messages(queue):
            runtimes.extend(parallel(lambda ev: time_fn(handler, ev, {}), events))
            queue.delete_messages(Entries=receipts)
            pbar.update(len(events))
    # this is going to imprecise with cached responses...
    print('took {:.2f}ms on avg'.format(sum(runtimes)/len(runtimes)))


def sqs_as_sns(message):
    # <http://docs.aws.amazon.com/lambda/latest/dg/eventsources.html#eventsources-sns>
    return {
        'Records': [{
            'Sns': message
        }]
    }


def time_fn(fn, *args, **kwargs):
    """times a function execution in ms"""
    start = time.time()
    fn(*args, **kwargs)
    return (time.time() - start) * 1000


# <https://github.com/spulec/moto/issues/1026>
@mock_s3
@mock_sns
@mock_sqs
def test():
    # so we don't constantly hit the sites
    requests_cache.install_cache('/tmp/vizlab.cache')

    # reset redis (optional)
    r.flushdb()

    # clean up test data
    session = Session()
    session.query(ImageUsage).delete()
    session.query(Image).delete()
    session.query(Context).delete()
    session.commit()
    assert session.query(Image).count() == 0
    assert session.query(ImageUsage).count() == 0
    assert session.query(Context).count() == 0

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

    sqs = boto3.resource('sqs')
    sqs_client = boto3.client('sqs')

    queues = {}
    for name, topic_arn in topics.items():
        queue_url, queue_arn = create_queue(sqs_client, name)
        queue = sqs.Queue(queue_url)
        sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='sqs',
            Endpoint=queue_arn)
        queues[name] = queue

    # setup mock s3
    bucket_name = 'vizlab-imgs-test'
    s3 = boto3.resource('s3')
    s3.create_bucket(Bucket=bucket_name)
    bucket = s3.Bucket(bucket_name)
    os.environ['s3_bucket'] = bucket_name

    start = time.time()

    print('arbiter...')
    os.environ['sns_arn'] = topics['arbiter']
    handlers['arbiter']({}, {})

    print('scraper...')
    os.environ['sns_arn'] = topics['scraper']
    process_queue(handlers['scraper'], queues['arbiter'])

    print('parser...')
    os.environ['sns_arn'] = topics['parser']
    process_queue(handlers['parser'], queues['scraper'])
    assert session.query(Context).count() > 0

    print('downloader...')
    process_queue(handlers['downloader'], queues['parser'])
    assert session.query(Image).count() > 0
    assert session.query(ImageUsage).count() > 0

    # TODO check mock s3
    images = session.query(Image).all()
    keys = [obj.key for obj in bucket.objects.all()]
    assert set(keys) == set([img.hash for img in images])

    print('images:', session.query(Image).count())
    print('usages:', session.query(ImageUsage).count())
    print('contexts:', session.query(Context).count())
    print('done')
    print('took {}s'.format(time.time() - start))


if __name__ == '__main__':
    test()