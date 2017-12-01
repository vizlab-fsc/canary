"""
4chan/8chan
reference <https://github.com/4chan/4chan-API/blob/master/README.md>
"""

import logging
import requests
from itertools import chain
from json import JSONDecodeError
from lib import config

logger = logging.getLogger(__name__)


def _request(url):
    res = requests.get(url, headers={'User-Agent': config.USER_AGENT})
    try:
        return res.json()
    except JSONDecodeError:
        logger.error('JSONDecodeError on {}, response was: "{}"'.format(url, res.text))
        return None


class Chan():
    domain = None
    base = None
    thread_path = None

    def __init__(self, board):
        self.board = board

    @property
    def id(self):
        return '{}:{}'.format(self.domain, self.board)

    def _get_thread(self, id):
        """get thread data"""
        url = '{}/{}/{}/{}.json'.format(self.base, self.board, self.thread_path, id)
        return _request(url)

    def query_threads(self):
        """gets a list of pages of thread metadata.
        the metadata for each thread is an id and last modified epoch"""
        url = '{}/{}/threads.json'.format(self.base, self.board)
        return _request(url)

    def thread_ids(self):
        """compute which threads need to update,
        given an existing set of threads"""
        thread_meta_pages = self.query_threads()
        thread_meta = chain.from_iterable([p['threads'] for p in thread_meta_pages])
        ids = [meta['no'] for meta in thread_meta]
        return ids

    def get_posts(self):
        posts = [self.get_thread(id) for id in self.thread_ids()]
        return list(chain.from_iterable(posts))

    def get_thread(self, id):
        """fetch thread details"""
        thread = self._get_thread(id)
        if thread is None:
            return str(id), None
        return [self.parse_post(p) for p in thread['posts']]

    def parse_post(self, post):
        if 'tim' in post:
            attachments = [self.attach_fmt.format(self.board, post['tim'], post['ext'])]
        else:
            attachments = []
        return {
            'lid': post['no'],
            'author': post.get('id'),
            'attachments': attachments,
            'context': post.get('com'),
            'created_at': post['time'],
            'url': self.permalink_fmt.format(self.board, post['resto'], post['no'])
        }


class FourChan(Chan):
    domain = '4chan.org'
    base = 'https://api.4chan.org'
    thread_path = 'thread'
    attach_fmt = 'http://i.4cdn.org/{}/{}{}'
    permalink_fmt = 'http://boards.4chan.org/{}/thread/{}#p{}'


class EightChan(Chan):
    domain = '8ch.net'
    base = 'https://8ch.net'
    thread_path = 'res'
    attach_fmt = 'https://8ch.pl/{}/src/{}{}'
    permalink_fmt = 'https://8ch.pl/{}/res/{}.html#q{}'
