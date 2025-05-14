import pandas as pd
import numpy as np
from datetime import datetime

# Preprocess stock data for model training and prediction
def preprocess_data(stock_data):
    if not stock_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(stock_data)
    
    # Ensure date is in datetime format
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort by date
    df = df.sort_values('date')
    
    # Calculate additional technical indicators
    df = add_technical_indicators(df)
    
    # Fill any missing values
    df = df.fillna(method='ffill').fillna(method='bfill')
    
    # Drop any remaining NaN values
    df = df.dropna()
    
    return df

# Add technical indicators to the DataFrame.
def add_technical_indicators(df):

    df = df.copy()  #Make a copy to avoid modifying the original DataFrame
    
    # Moving Averages
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['ma50'] = df['close'].rolling(window=50).mean()
    
    # Exponential Moving Averages
    df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
    
    # MACD (Moving Average Convergence Divergence)
    df['macd'] = df['ema12'] - df['ema26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    
    # RSI (Relative Strength Index)
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['20sd'] = df['close'].rolling(window=20).std()
    df['upper_band'] = df['ma20'] + (df['20sd'] * 2)
    df['lower_band'] = df['ma20'] - (df['20sd'] * 2)
    
    # Daily Returns
    df['daily_return'] = df['close'].pct_change()
    
    # Volatility (20-days standard deviation of returns)
    df['volatility'] = df['daily_return'].rolling(window=20).std()
    
    # Trading Volume Features
    df['volume_ma5'] = df['volume'].rolling(window=5).mean()
    
    return df

# Normalize selected features in the DataFrame
def normalize_data(df, feature_columns):
    df_norm = df.copy()
    
    for column in feature_columns:
        if column in df.columns:
            min_val = df[column].min()
            max_val = df[column].max()
            range_val = max_val - min_val
            
            if range_val > 0:  # Avoid division by zero
                df_norm[column] = (df[column] - min_val) / range_val
            else:
                df_norm[column] = 0
    
    return df_norm

# Create sequences for time series prediction
def create_sequences(data, seq_length):
    X, y = [], []
    
    for i in range(len(data) - seq_length):
        X.append(data[i:i + seq_length])
        y.append(data[i + seq_length])
    
    return np.array(X), np.array(y)