import os
import sys
import argparse
import pandas as pd
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.model import StockPredictionModel
from utils.data_fetcher import PolygonDataFetcher
from utils.preprocessor import preprocess_data
from config import POLYGON_API_KEY

 # Train a ML model for a given ticker.
def train_model(ticker, start_date=None, end_date=None, save_path=None):
    print(f"Training model for {ticker}...")
    
    # Set default dates if not provided
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    if start_date is None:
        # Default to 3 years of data for training
        start_date = (datetime.now() - timedelta(days=365*3)).strftime('%Y-%m-%d')
    
    # Set default save path if not provided
    if save_path is None:
        save_path = os.path.join('models', 'saved_models', f"{ticker}_model.h5")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Initialize data fetcher
    data_fetcher = PolygonDataFetcher(POLYGON_API_KEY)
    
    print(f"Fetching historical data for {ticker} from {start_date} to {end_date}...")
    # Fetch historical data
    historical_data = data_fetcher.get_stock_data(ticker, start_date, end_date)
    
    if not historical_data:
        print(f"Error: No data found for {ticker}")
        return None
    
    print(f"Retrieved {len(historical_data)} data points.")
    
    # Preprocess data
    print("Preprocessing data...")
    processed_data = preprocess_data(historical_data)
    
    # Initialize and train model
    print("Training model...")
    model = StockPredictionModel(ticker)
    model.train(processed_data)
    
    # Save model
    print(f"Saving model to {save_path}...")
    model.save(save_path)
    
    print("Model training complete!")
    return model

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Train stock prediction model')
    parser.add_argument('ticker', type=str, help='Stock ticker symbol')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--save-path', type=str, help='Path to save model')
    
    args = parser.parse_args()
    
    # Train model
    train_model(args.ticker, args.start_date, args.end_date, args.save_path)

if __name__ == '__main__':
    main()