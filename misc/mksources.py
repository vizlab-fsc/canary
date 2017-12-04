from lib.models import Source, Session

SOURCES = ['4chan:pol', '8chan:leftypol']

session = Session()
for name in SOURCES:
    source = session.query(Source).filter(Source.name==name).first()
    if source is None:
        source = Source(name=name)
        session.add(source)
session.commit()
