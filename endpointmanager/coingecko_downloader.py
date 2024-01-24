""" CoinGecko Downloader """

from collections import namedtuple

import requests
import datetime


EndpointResponse = namedtuple("endpointdata", ["json", "encoding", "reason"])

class CoingeckoDownloader(object):
    """ Coingecko Downloader Base """

    BASE_URL = "https://api.coingecko.com/api/v3/"

    def get_endpoint_data(self, uri=None):
        """ Retrieve CoinGecko Endpoint Data """

        res = requests.get(self.BASE_URL + uri, timeout=20)

        if not res.status_code == 200:
            yield EndpointResponse(None, res.apparent_encoding, res.reason)

        yield EndpointResponse(
            res.json(),
            res.apparent_encoding,
            res.reason
        )


class CoingeckoHistory(CoingeckoDownloader):
    """ Coingecko History """

    def __init__(self):
        self.apikey = ""

    def get_endpoint_data(self, coin=None, date=None):
        if coin is None:
            return

        if date is None:
            d = datetime.datetime.now()
            date = "{}-{}-{}".format(
                d.month, d.day, d.year
            )

        return super(CoingeckoHistory, self).get_endpoint_data(
            uri=f"coins/{coin}/history?date={date}"
        )
