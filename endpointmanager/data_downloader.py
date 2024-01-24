import requests
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from utils.serialize import SerializeJSON
from .endpoint import Endpoint
from .alphavantage_downloader import *
from .coingecko_downloader import *
from .financialmodelingprep_downloader import *
from Models import (CryptoList)

import traceback

def is_recoverable_error(error):
    return any(
        (
            isinstance(error, requests.RequestException),
            isinstance(error, requests.packages.urllib3.exceptions.ReadTimeoutError),
        )
    )

class DownloadData(object):
    FAILED_DOWNLOAD_CRYPTO = "FAILED_DOWNLOAD_CRYPTO"



def download(endpoint, app):
    # if not isinstance(endpoint, Endpoint):
    #     return

    # runners = [
    #     endpoint[0].get_endpoint(),
    #     endpoint[1].get_endpoint(),
    #     endpoint[2].get_endpoint(),
    #     endpoint[3].get_endpoint(),
    #     endpoint[4].get_endpoint()
    # ]

    # with ThreadPoolExecutor(max_workers=5) as e:
    #     for apiendpoint in runners:
    #         try:
    #             f = e.submit(apiendpoint.get_endpoint_data)
    #             t = f.result()
    #             return SerializeJSON(t.endpointdata) # this is what's returned to html
    #             print(t.endpointdata)
    #         except:
    #             pass

    #runner = AlphaVangtageExchangeRate()
    
    runner = FinancialModelingPrepHistoricalPriceFull()

    with app.app_context():
        active_coins = CryptoList.get_active_coins()  # Retrieve active coins

    results = []
    
    if len(active_coins) < 1:
        print(f"No Active coins available")
        return
    
    with ThreadPoolExecutor(max_workers=len(active_coins)) as executor:
        # Create a future for each active coin
        
        future_to_coin = {executor.submit(runner.get_endpoint_data, coin=coin, app=app): coin for coin in active_coins}
        
        for future in concurrent.futures.as_completed(future_to_coin):
            coin = future_to_coin[future]
            try:
                print("here 1")
                generator_object = future.result()
                print("here 2")
                if generator_object is not None:
                    try:
                        endpoint_data = next(generator_object)
                        results.append(endpoint_data)
                        print(f"Data for {coin}:", endpoint_data)
                    except StopIteration:
                        print(f"No data yielded from generator for {coin}")
            except Exception as e:
                print(f"Exception occurred while downloading data for {coin}: {e}")
                traceback.print_exc()  # This will print the traceback of the exception

    return results



    # with ThreadPoolExecutor(active_coins) as e:
    #     f = e.submit(runner.get_endpoint_data, coin="BTC")
        
    #     generator_object = f.result()
        
    #     if generator_object is not None:
    #         try:
    #             endpoint_data = next(generator_object)
    #             print(endpoint_data)
    #             return endpoint_data
    #         except StopIteration:
    #             print("no Data yielded from generator")
    #             return None
    # return None


