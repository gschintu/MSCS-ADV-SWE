""" Financial Model Downloader """

from collections import namedtuple

import requests

from Models import (ApiFMPHistoricalPriceFull, CryptoList)
from utils.serialize import SerializeJSON

import json

EndpointResponse = namedtuple("endpointdata", ["json", "encoding", "reason"])


class FinancialModelingPrepDownloader(object):
    """ Dowloader for Financial Modeling Prep """

    BASE_URL = "https://financialmodelingprep.com/api/v3/"

    def get_endpoint_data(self, uri=None, **kwargs):
        """ Get FMP Endpoint Data """
        coin = kwargs.get('coin')
        app = kwargs.get('app')

        # this is coming from sub class like FinancialModelingPrepHistoricalPriceFull
        if coin is None:
            print("base class coin parameter is none")
            return
        
        print(f"FMP endpoint URL is: {self.BASE_URL + uri}")
        res = requests.get(self.BASE_URL + uri, timeout=20)

        if not res.status_code == 200:
            yield EndpointResponse(None, res.apparent_encoding, res.reason)

        #data = SerializeJSON(res.json())
        with app.app_context():
            ApiFMPHistoricalPriceFull.update_historical_data(res, coin.code)

        yield EndpointResponse(
            None,
            res.apparent_encoding,
            res.reason
        )


class FinancialModelingPrepHistoricalPriceFull(FinancialModelingPrepDownloader):
    """ Financial Modeling History Downloader """

    def __init__(self):
        self.apikey = "0xXrNFzXen9yuK6aVKJ0mRDmS6nuujmS"

    def get_endpoint_data(self, **kwargs):
        """ Get Endpoint Data """

        coin = kwargs.get('coin')
        if coin is None:
            return
        
        app = kwargs.get('app')
        if app is None:
            return

        with app.app_context():
            api_coin_id = CryptoList.get_api_coin_id(coin_code=coin.code, field_id="code_FMP")
            if isinstance(api_coin_id, list):
                api_coin_id = api_coin_id[0][0] #could improve, but for now get_api_coin_id returns list of tuple

            print(f"coin_id for FMP api is: {api_coin_id}")
        return super(FinancialModelingPrepHistoricalPriceFull, self).get_endpoint_data(
            uri=f"historical-price-full/{api_coin_id}?apikey={self.apikey}", coin=coin, app=app
        )
