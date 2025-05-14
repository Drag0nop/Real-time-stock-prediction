# Real-time-stock-prediction

This document outlines the structure and implementation of a web application for stock market prediction using Flask, HTML/CSS/JavaScript, and a machine learning model.

## Project Structure

```
stock_prediction_app/
├── app.py                  # Flask main application file
├── config.py               # Configuration settings (API keys, etc.)
├── requirements.txt        # Python dependencies
├── static/                 # Static files
│   ├── css/
│   │   └── style.css       # CSS styling
│   ├── js/
│   │   └── main.js         # JavaScript for frontend functionality
│   └── img/                # Images (if needed)
├── templates/
│   └── index.html          # Main HTML template
├── models/
│   ├── model.py            # ML model definition
│   ├── train.py            # Model training script
│   └── saved_models/       # Directory to store trained models
└── utils/
    ├── data_fetcher.py     # Polygon.io API integration
    └── preprocessor.py     # Data preprocessing utilities
```

## Implementation Details

### 1. Backend (Flask)

We use Flask to create a RESTful API that serves predictions and handles stock data requests. The main endpoint is `/api/predict`, which accepts a stock ticker symbol and prediction period (1, 5, 15, or 30 days) and returns the predicted stock prices.

### 2. Frontend (HTML, CSS, JavaScript)

The frontend is clean and focused with a stock selection input, prediction buttons for different time periods (1, 5, 15, and 30 days), and visualization of predictions using Chart.js. The UI displays both historical data and predicted future prices.

### 3. Machine Learning Model

We implement an LSTM (Long Short-Term Memory) neural network model for time series prediction. The model:
- Uses 60 days of historical data as input sequence
- Includes multiple LSTM layers with dropout for regularization
- Is trained on historical stock data from Polygon.io
- Outputs predictions for the specified number of days ahead

### 4. Stock Data

We use Polygon.io API to fetch historical stock data for training and real-time data for predictions. The data is preprocessed to include technical indicators like moving averages, RSI, MACD, and Bollinger Bands to improve prediction accuracy.

## Setup Instructions

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Get a Polygon.io API key from https://polygon.io/dashboard
4. Update `config.py` with your API key:
   ```python
   POLYGON_API_KEY = "YOUR_API_KEY_HERE"
   ```
5. Run the application:
   ```
   python app.py
   ```
6. Open your browser and navigate to http://localhost:5000

## Usage

1. Enter a stock ticker symbol (e.g., AAPL, MSFT, GOOGL)
2. Select a prediction period (1, 5, 15, or 30 days)
3. Click the "Predict" button
4. View the prediction results in the chart and summary cards

## Machine Learning Model Training

To train a model for a specific stock:

```
python models/train.py TICKER_SYMBOL
```

Example:
```
python models/train.py AAPL
```

This will fetch historical data, train an LSTM model, and save it to the `models/saved_models/` directory.
