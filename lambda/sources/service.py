import os
from lib.models import Source, Session


def handler(event, context):
    """
    (should run on a schedule)
    1. sends out sources for other functions to update
    """
    sources = [s.strip() for s in os.environ['SOURCES'].split(',')]
    session = Session()
    for name in sources:
        source = Source(name=name)
        session.add(source)
        session.commit()
    session.close()
    return sources
