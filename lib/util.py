import json


def parse_sns_event(ev):
    # <http://docs.aws.amazon.com/lambda/latest/dg/eventsources.html#eventsources-sns>
    return json.loads(ev['Records'][0]['Sns']['Message'])
