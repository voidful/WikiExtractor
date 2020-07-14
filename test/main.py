import unittest
from wiki import *


class Test(unittest.TestCase):

    def test_wiki_load_not_exist(self):
        self.assertRaises(FileNotFoundError, WikiDump, 'abc')

    def test_check_outdated(self):
        wiki = WikiDump("zhwiki")
        self.assertTrue(wiki.check_outdated() is False)


if __name__ == '__main__':
    unittest.TestFile()
