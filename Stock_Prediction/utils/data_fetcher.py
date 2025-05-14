import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# Class to fetch stock data from Polygon.io API
class PolygonDataFetcher:
    
    BASE_URL = "https://api.polygon.io"
    
    def __init__(self, api_key):

        self.api_key = api_key
    
    # Fetch historical stock data from Polygon.io
    def get_stock_data(self, ticker, start_date, end_date, timespan='day'):

        endpoint = f"{self.BASE_URL}/v2/aggs/ticker/{ticker}/range/1/{timespan}/{start_date}/{end_date}"
        params = {
            'apiKey': self.api_key,
            'sort': 'asc',  # Sort results in ascending order by timestamp
            'limit': 50000  # Max number of results
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            data = response.json()
            
            if 'results' not in data or not data['results']:
                print(f"No data returned for {ticker} from {start_date} to {end_date}")
                return []
            
            # Process the results
            results = data['results']
            processed_results = []
            
            for item in results:
                processed_item = {
                    'date': self._timestamp_to_date(item['t']),
                    'open': item['o'],
                    'high': item['h'],
                    'low': item['l'],
                    'close': item['c'],
                    'volume': item['v'],
                    'timestamp': item['t']
                }
                processed_results.append(processed_item)
            
            return processed_results
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Polygon.io: {e}")
            return []
    
    # Search for tickers matching a query
    def search_tickers(self, query):
        endpoint = f"{self.BASE_URL}/v3/reference/tickers"
        params = {
            'apiKey': self.api_key,
            'search': query,
            'active': 'true',
            'sort': 'ticker',
            'order': 'asc',
            'limit': 10
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' not in data or not data['results']:
                return []
            
            # Extract ticker symbols and names
            results = [
                {
                    'ticker': item['ticker'],
                    'name': item['name'],
                    'market': item.get('market', 'Unknown'),
                    'locale': item.get('locale', 'Unknown')
                }
                for item in data['results']
            ]
            
            return results
        
        except requests.exceptions.RequestException as e:
            print(f"Error searching tickers: {e}")
            return []
    
    # Get detailed info about company.
    def get_company_details(self, ticker):
        endpoint = f"{self.BASE_URL}/v3/reference/tickers/{ticker}"
        params = {
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' not in data:
                return None
            
            return data['results']
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching company details: {e}")
            return None
    
    # Convert millisecond timestamp to date string
    def _timestamp_to_date(self, timestamp_ms):

        date = datetime.fromtimestamp(timestamp_ms / 1000)
        return date.strftime('%Y-%m-%d')