from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from models.model import StockPredictionModel
from utils.data_fetcher import PolygonDataFetcher
from utils.preprocessor import preprocess_data
from config import POLYGON_API_KEY

app = Flask(__name__)

# Initialize data_fetcher with API key
data_fetcher = PolygonDataFetcher(POLYGON_API_KEY)

# Global variables
MODEL_PATH = 'models/saved_models/'
default_ticker = 'AAPL'  # Default stock ticker

@app.route('/')
def index():
    #Render the main page
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    # API endpoint for stock predictions
    data = request.get_json()
    ticker = data.get('ticker', default_ticker).upper()
    days = int(data.get('days', 30))
    
    # Validate input
    if days not in [1, 5, 15, 30]:
        return jsonify({'error': 'Invalid prediction days. Choose from 1, 5, 15, or 30 days.'}), 400
    
    try:
        # Get historical data for the selected ticker
        end_date = datetime.now()
        # Get data for the past year for training/context
        start_date = end_date - timedelta(days=365)
        
        # Format dates for Polygon API
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # Fetch historical data
        historical_data = data_fetcher.get_stock_data(ticker, start_date_str, end_date_str)
        
        if not historical_data or len(historical_data) < 60:  # Need sufficient data for prediction
            return jsonify({'error': 'Insufficient historical data for prediction'}), 400
        
        # Preprocess data
        processed_data = preprocess_data(historical_data)
        
        # Load or create model
        model_file = os.path.join(MODEL_PATH, f"{ticker}_model.h5")
        
        if os.path.exists(model_file):
            # Load existing model
            model = StockPredictionModel(ticker)
            model.load(model_file)
        else:
            # Create and train new model
            model = StockPredictionModel(ticker)
            model.train(processed_data)
            model.save(model_file)
        
        # Make prediction
        predictions = model.predict(processed_data, days)
        
        # Format results
        dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, days + 1)]
        
        results = {
            'ticker': ticker,
            'predictions': [
                {'date': date, 'price': float(price)} 
                for date, price in zip(dates, predictions)
            ],
            'historical': [
                {'date': row['date'], 'price': row['close']} 
                for row in historical_data[-30:]  # Historical data of last 30 days
            ]
        }
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create directory for models if it doesn't exist
    os.makedirs(MODEL_PATH, exist_ok=True)
    app.run(debug=True)