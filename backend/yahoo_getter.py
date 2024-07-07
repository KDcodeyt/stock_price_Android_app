import requests
import pandas as pd
from datetime import datetime
import time
import os

def get_unix_timestamp(date_str):
    return int(time.mktime(datetime.strptime(date_str, "%Y-%m-%d").timetuple()))

def get_yahoo_finance_data(stock_id, start, end, max_retries=5):
    start_timestamp = get_unix_timestamp(start)
    end_timestamp = get_unix_timestamp(end)
    
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{stock_id}"
    
    params = {
        "period1": start_timestamp,
        "period2": end_timestamp,
        "interval": "1d",
        "events": "history",
        "includeAdjustedClose": "true"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, headers=headers, verify=False)  # Verify is set to False to ignore SSL certificate errors (not recommended for production code
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            
            # Save response to a CSV file
            csv_path = f"{stock_id}.csv"
            with open(csv_path, 'w') as f:
                f.write(response.text)
            
            # Read the CSV file into a DataFrame
            df = pd.read_csv(csv_path)
            return df
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Too Many Requests
                print(f"Rate limit exceeded. Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
    raise Exception(f"Failed to retrieve data after {max_retries} attempts")

# Example usage
stock_id = "GOOG"
start_date = "2023-01-01"
end_date = "2023-12-31"

# data = get_yahoo_finance_data(stock_id, start_date, end_date)
# print(data.head())
