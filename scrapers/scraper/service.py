from lib.domains import chan


def handler(event, context):
    id = event.get('id')
    domain = event.get('domain')

    if domain == 'chan:pol':
        pol = chan.four('pol')
        return chan.get_thread(pol, id)
