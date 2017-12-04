import redis
from datetime import datetime, timedelta

EXPIRES = 2 # in days
r = redis.StrictRedis() # TODO connection string


def record_seen(domain, posts):
    """record which post
    have been seen for a domain"""
    if posts:
        ts = datetime.utcnow().timestamp()
        kwargs = {p['lid']: ts for p in posts}
        r.zadd(domain, **kwargs)


def record_downloaded(url):
    """record which images
    have been downloaded"""
    ts = datetime.utcnow().timestamp()
    r.zadd('images', **{url: ts})


def already_downloaded(url):
    return r.zscore('images', url) is not None


def filter_seen(domain, posts):
    """filter out posts that
    have already been seen"""
    # TODO can we bulk lookup?
    return filter(lambda p: r.zscore(domain, p['lid']) is None, posts)


def prune(domain):
    """removes members from set with a score (timestamp)
    older than EXPIRES days before now"""
    cutoff = datetime.utcnow() - timedelta(days=EXPIRES)
    r.zremrangebyscore(domain, 0, cutoff.timestamp())
