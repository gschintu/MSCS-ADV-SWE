""" Endpoints  """

from .endpoints import (
    ALPHAVANTAGE_ENDPOINTS,
    COINGECKO_ENDPOINTS
)

class Endpoint(object):

    def __init__(self, endpoint):
        self.endpoint = endpoint
    
    def get_endpoint(self):
        return ALPHAVANTAGE_ENDPOINTS.get(self.endpoint)