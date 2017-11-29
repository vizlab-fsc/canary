"""
4chan/8chan
reference <https://github.com/4chan/4chan-API/blob/master/README.md>
"""

import logging
import requests
from itertools import chain
from datetime import datetime
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
    def __init__(self, base, thread_path, board):
        self.base = base
        self.board = board
        self.thread_path = thread_path

    def _get_thread(self, id):
        """get thread data"""
        url = '{}/{}/{}/{}.json'.format(self.base, self.board, self.thread_path, id)
        return _request(url)

    def query_threads(self):
        """gets a list of pages of thread metadata.
        the metadata for each thread is an id and last modified epoch"""
        url = '{}/{}/threads.json'.format(self.base, self.board)
        return _request(url)

    def threads_to_update(self, threads):
        """compute which threads need to update,
        given an existing set of threads"""
        thread_meta_pages = self.query_threads()
        thread_meta = chain.from_iterable([p['threads'] for p in thread_meta_pages])
        to_update = []
        for meta in thread_meta:
            id = meta['no']
            last_modified = meta['last_modified']

            # str because keys become strings in json
            if str(id) not in threads:
                to_update.append((id, last_modified))
            else:
                thread = threads[str(id)]
                if 'last_modified' not in thread or last_modified > thread['last_modified']:
                    to_update.append((id, last_modified))
        return to_update


    def get_thread(self, id):
        """fetch thread details"""
        thread = self._get_thread(id)
        if thread is None:
            return str(id), None
        return str(id), {
            'posts': thread['posts'],
            'last_modified': datetime.utcnow().timestamp()
        }


def four(board):
    return Chan('https://api.4chan.org', 'thread', board)


def eight(board):
    return Chan('https://8ch.net', 'res', board)
