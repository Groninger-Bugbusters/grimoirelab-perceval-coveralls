import os
import unittest
import unittest.mock

import httpretty
import pkg_resources

pkg_resources.declare_namespace('perceval.backends')

from perceval.backend import BackendCommandArgumentParser
from perceval.backends.coverage.coveralls import (CATEGORY_TEST_COVERAGE,
                                                  Coveralls, CoverallsCommand)


COVERALLS_BASE_URL = "https://coveralls.io/"
MOCK_REPO = 'github/user/repo'


def setup_http_server(repo=MOCK_REPO, status=200):
    """Setup mock HTTP server"""

    # Register URLs for retrieving three pages.
    for page_num in range(1, 4):
        builds_page = read_file(f'data/coveralls/builds_page_{page_num}.json')
        httpretty.register_uri(
            httpretty.GET,
            f'{COVERALLS_BASE_URL}{repo}.json?page={page_num}',
            body=builds_page, status=status)


def read_file(filename, mode='r'):
    dirname = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(dirname, filename)
    with open(file_path, mode, encoding = 'utf-8') as file:
        content = file.read()
    return content


class TestCoverallsBackend(unittest.TestCase):
    """Coveralls backend unit tests"""

    @httpretty.activate
    def test_initialization(self):
        """Test whether attributes are initializated"""

        coveralls = Coveralls(MOCK_REPO, tag='test')

        self.assertEqual(coveralls.repo, MOCK_REPO)
        self.assertEqual(coveralls.tag, 'test')
        self.assertIsNone(coveralls.client)
        self.assertTrue(coveralls.ssl_verify)

        # When tag is empty or None it will be set to the repo
        coveralls = Coveralls(MOCK_REPO, ssl_verify=False)
        self.assertEqual(coveralls.repo, MOCK_REPO)
        self.assertEqual(coveralls.tag, MOCK_REPO)
        self.assertFalse(coveralls.ssl_verify)

        coveralls = Coveralls(MOCK_REPO, tag='')
        self.assertEqual(coveralls.repo, MOCK_REPO)
        self.assertEqual(coveralls.tag, MOCK_REPO)

    def test_has_archiving(self):
        """Test if it returns True when has_archiving is called"""

        self.assertFalse(Coveralls.has_archiving())

    def test_has_resuming(self):
        """Test if it returns False when has_resuming is called"""

        self.assertFalse(Coveralls.has_resuming())

    @httpretty.activate
    def test_fetch_builds(self):
        """Test whether items are properly fetched from Coveralls"""

        setup_http_server()
        coveralls = Coveralls(MOCK_REPO)
        builds = [builds for builds in coveralls.fetch(CATEGORY_TEST_COVERAGE)]

        self.assertEqual(len(builds), 15)

        # Check the first result of each page (from page 3 to 1).
        expected_commit_shas = [
            '47891c0d6dd2512169bb9c8d1c0eca5ddda5ee9b',
            'eed8d1d332eb3a8385188a0a32dcadc9c032a924',
            'ba19bfd5e40bffdd422ca8e68526326b47f97491'
        ]

        for i in range(0, len(builds), 5):
            build = builds[i]
            self.assertEqual(
                build['data']['commit_sha'], expected_commit_shas[int(i/5)])
            self.assertEqual(build['origin'], MOCK_REPO)
            self.assertEqual(build['category'], CATEGORY_TEST_COVERAGE)
            self.assertEqual(build['tag'], MOCK_REPO)

    @httpretty.activate
    def test_search_fields(self):
        """Test whether the search_fields is properly set"""

        setup_http_server()
        coveralls = Coveralls(MOCK_REPO)
        builds = [builds for builds in coveralls.fetch(CATEGORY_TEST_COVERAGE)]

        # Check the first result of each page (from page 3 to 1).
        for i in range(0, len(builds), 5):
            build = builds[i]
            self.assertEqual(
                build['data']['commit_sha'], build['search_fields']['item_id'])


class TestCoverallsCommand(unittest.TestCase):
    "CoverallsCommand unit tests"

    def test_backend_class(self):
        """Test if the backend class is Coveralls"""

        self.assertIs(CoverallsCommand.BACKEND, Coveralls)

    def test_setup_cmd_parser(self):
        """Test if the parser object is correctly initialized"""

        parser = CoverallsCommand.setup_cmd_parser()
        self.assertIsInstance(parser, BackendCommandArgumentParser)
        self.assertEqual(parser._backend, Coveralls)

        args = [MOCK_REPO]

        parsed_args = parser.parse(*args)
        self.assertEqual(parsed_args.repo, MOCK_REPO)


if __name__ == "__main__":
    unittest.main(warnings='ignore')
