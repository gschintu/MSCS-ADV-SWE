""" AlphaVantage Downloader """

from collections import namedtuple

import requests

EndpointResponse = namedtuple("endpointdata", ["json", "encoding", "reason"])

class AlphaVangtageDownloader(object):
    """ AlphaVantage Downloader Base """

    BASE_URL = "https://www.alphavantage.co/query?"

    def get_endpoint_data(self, uri=None):
        """ Get AlphaVantage Data """

        res = requests.get(self.BASE_URL + uri, timeout=20)

        if not res.status_code == 200:
            yield EndpointResponse(None, res.apparent_encoding, res.reason)    

        yield EndpointResponse(
            res.json(),
            res.apparent_encoding,
            res.reason
        )


class AlphaVangtageExchangeRate(AlphaVangtageDownloader):
    """ Get AlphaVantage Data """

    def __init__(self):
        self.apikey = "7HWS4528GA0TMNX2"

    def get_endpoint_data(self, uri=None, coin=None):
        """ Get AV Data """

        if coin is None:
            return 

        return super(AlphaVangtageExchangeRate, self).get_endpoint_data(
            uri=f"function=CURRENCY_EXCHANGE_RATE&from_currency={coin}&to_currency=USD&apikey={self.apikey}"
        )
