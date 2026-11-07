import argparse
import logging
import os
from dotenv import load_dotenv
import requests
import time

"""
Skeleton for Squirro Delivery Hiring Coding Challenge
November 2025
"""

log = logging.getLogger(__name__)
load_dotenv()
NY_TIMES_KEY = os.getenv("NY_TIMES_KEY")
NY_TIMES_URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
MAX_RETRIES = 5
RETRY_CODES = {429, 500, 502, 503, 504}
MAX_PAGE = 1
PAGE_DELAY = 2


class NYTimesSource(object):
    """
    A data loader plugin for the NY Times API.
    """

    def __init__(self):
        self.schema = set()
        self.inc_column = None
        self.max_inc_value = None

    def connect(self, inc_column=None, max_inc_value=None):
        """Connect to the source"""
        log.debug("Incremental Column: %r", inc_column)
        log.debug("Incremental Last Value: %r", max_inc_value)
        self.inc_column = inc_column
        self.max_inc_value = max_inc_value

    def disconnect(self):
        """Disconnect from the source."""
        # Nothing to do
        pass

    def flatten(self, d, parent_key=""):
        """
        Flatten nested dictionaries into one level with dotted keys.
        Lists and empty dictionaries are kept as values.
        :returns The flattened dictionary
        """
        result = {}
        for key, value in d.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict) and value:
                result.update(self.flatten(value, new_key))
            else:
                result[new_key] = value
        return result

    def fetch_page(self, params):
        """
        Request one page from the API, retrying on rate limits and server errors.
        :returns The parsed JSON response
        """
        for attempt in range(MAX_RETRIES):
            req = requests.get(NY_TIMES_URL, params=params)
            if req.status_code not in RETRY_CODES:
                return req.json()
            log.warning("Status code: %s", req.status_code)
            time.sleep(60)

    def getDataBatch(self, batch_size):
        """
        Generator - Get data from source on batches.
        :returns One list for each batch. Each of those is a
        list of
        dictionaries with the defined rows.
        """

        params = {"q": self.args.query, "api-key": self.args.api_key}
        if self.inc_column == "pub_date" and self.max_inc_value:
            params["begin_date"] = self.max_inc_value[:10].replace("-", "")
            params["sort"] = "oldest"
        batch = []
        for page in range(MAX_PAGE + 1):
            if page > 0:
                time.sleep(PAGE_DELAY)
            params["page"] = page
            docs = self.fetch_page(params)["response"]["docs"]
            if not docs:
                break
            for doc in docs:
                flat_doc = self.flatten(doc)
                if self.inc_column and self.max_inc_value:
                    # begin_date only filters by day, so skip what we already have
                    if flat_doc.get(self.inc_column, "") <= self.max_inc_value:
                        continue
                self.schema.update(flat_doc)
                batch.append(flat_doc)
                if len(batch) == batch_size:
                    yield batch
                    batch = []
        if batch:
            yield batch

    def getSchema(self):
        """
        Return the schema of the dataset
        :returns a List containing the names of the columns
        retrieved from the
        source
        """

        return sorted(self.schema)


if __name__ == "__main__":
    config = {
        "api_key": NY_TIMES_KEY,
        "query": "Silicon Valley",
    }

    source = NYTimesSource()
    # This looks like an argparse dependency - but the Namespace class is just
    # a simple way to create an object holding attributes.
    source.args = argparse.Namespace(**config)
    for idx, batch in enumerate(source.getDataBatch(3)):

        print(f"{idx} Batch of {len(batch)} items")
        for item in batch:
            print(f" - {item['_id']} - {item['headline.main']}")

    print(source.getSchema())
