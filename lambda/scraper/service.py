from lib.domains import chan


def handler(event, context):
    id = event.get('id')
    domain = event.get('domain')

    if domain == 'chan:pol':
        pol = chan.four('pol')
        return pol.get_thread(id)
