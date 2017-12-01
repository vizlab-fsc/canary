import unittest
from lib import parser


class ParserTests(unittest.TestCase):
    def test_image_url_parsing(self):
        content = 'Come on, OP. \
            This is a sub for content about dogs. \
            That\'s clearly a deer  \
            [here\'s some content anyway](https://i.imgur.com/Xx8YzCO.png) \
            and a relative free reference /rel/hello.png'
        urls = parser.image_urls(content)
        expected = [
            'https://i.imgur.com/Xx8YzCO.png',
            '/rel/hello.png'
        ]
        self.assertEqual(urls, expected)

    def test_is_image(self):
        urls = [
            'https://foo/bar.jpg',
            'https://foo/bar.jpg:large',
            'https://foo/bar.jpg?foo=bar',
            'https://foo/bar.jpg#foo'
        ]
        for url in urls:
            self.assertTrue(parser.is_image(url))
