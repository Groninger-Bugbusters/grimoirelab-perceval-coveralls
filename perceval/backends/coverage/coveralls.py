import logging
import time
from typing import List, Dict

import requests

from ...backend import (Backend,
                        BackendCommand,
                        BackendCommandArgumentParser,
                        DEFAULT_SEARCH_FIELD)
from ...client import HttpClient

COVERALLS_BASE_URL = "https://coveralls.io/"

CATEGORY_TEST_COVERAGE = "test_coverage"

logger = logging.getLogger(__name__)


class Coveralls(Backend):
    """Coveralls backend.

    This class allows you to retrieve the information on test coverage
    from coveralls for a repo.

    :param repo: The repo on coveralls to be retrieved,
        for example: github/chaoss/grimoirelab-perceval
    """

    version = '0.0.1'

    CATEGORIES = [CATEGORY_TEST_COVERAGE]

    def __init__(self, repo: str, tag=None, ssl_verify=True):
        origin = repo
        super().__init__(origin, tag=tag, ssl_verify=ssl_verify)
        self.repo = repo
        self.client = None

    def _init_client(self, from_archive=False):
        return HttpClient(COVERALLS_BASE_URL)

    def fetch_items(self, category, **kwargs):
        """Fetch the coverage report for each commit from coveralls.

        :param category: The category of items to fetch.
        :param kwargs: Arguments provided to the backend.

        :returns: a generator of coverage items.
        """
        logger.info("Fetching coveralls coverage for: %s", self.repo)

        build_coverages: List[Dict] = []

        resource_url = f"{COVERALLS_BASE_URL}{self.repo}.json"

        first_page_raw: requests.Response = self.client.fetch(f"{resource_url}?page=1")
        first_page = first_page_raw.json()

        build_coverages += first_page['builds']

        total_pages = first_page['pages']

        for page_number in range(2, total_pages + 1):
            page_raw: requests.Response = self.client.fetch(f"{resource_url}?page={page_number}")
            page = page_raw.json()
            build_coverages += page['builds']

        # Url returned is always None. Filter that out:
        for build in build_coverages:
            build.pop("url")

        # Add the moment when it was retrieved to the data:
        for build in build_coverages:
            build['retrieved_on'] = time.time()

        return build_coverages

    def search_fields(self, item) -> dict:
        """Adds search fields to an item.

        :param item: The item to extract the fields from.

        :returns: a dict of search fields.
        """

        return {DEFAULT_SEARCH_FIELD: self.metadata_id(item)}

    @classmethod
    def has_archiving(cls) -> bool:
        """Returns whether this backend supports archiving the items from the fetch process.

        :returns: False, this is not supported
        """
        return False

    @classmethod
    def has_resuming(cls) -> bool:
        """Returns whether this backend supports resuming the fetch process.

        :returns: False, this is not supported
        """
        return False

    @staticmethod
    def metadata_id(item) -> str:
        """Returns a metadata identifier for a coverage item

        :returns: a metadata identifier for the given item
        """
        return item['commit_sha']

    @staticmethod
    def metadata_category(item) -> str:
        """Returns the metadata category for this item.
        Seeing as this backend only generates one type of item, it's always the same.
        """
        return CATEGORY_TEST_COVERAGE

    @staticmethod
    def metadata_updated_on(item) -> time.struct_time:
        return item['retrieved_on']


class CoverallsCommand(BackendCommand):
    """Class to run the Coveralls backend from the CLI"""

    BACKEND = Coveralls

    @classmethod
    def setup_cmd_parser(cls):
        """Return the argument parser for Coveralls"""

        parser = BackendCommandArgumentParser(cls.BACKEND,
                                              token_auth=False,
                                              archive=False,
                                              ssl_verify=True)

        parser.parser.add_argument('repo', help="The repo to fetch the items for, example: "
                                                "github/chaoss/grimoirelab-perceval")
        return parser
