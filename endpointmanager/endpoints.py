
from .alphavantage_downloader import (
    AlphaVangtageExchangeRate
)

from .coingecko_downloader import (
    CoingeckoHistory,
    #CoingeckoMarkets,
    #CoingeckMarketChart
)

from .financialmodelingprep_downloader import (
    FinancialModelingPrepHistoricalPriceFull
)
ALPHAVANTAGE_ENDPOINTS = {
    'exchange_rate': AlphaVangtageExchangeRate()
}

COINGECKO_ENDPOINTS = {
    'history' : CoingeckoHistory(),
   # 'markets' : CoingeckoMarkets(),
   # 'market_chart' : CoingeckoMarketChart()
}

FINANCIALMODELINGPREP_ENDPOINTS = {
    'historical_FP' : FinancialModelingPrepHistoricalPriceFull()
}