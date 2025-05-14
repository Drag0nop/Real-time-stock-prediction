import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
import os
import joblib

class StockPredictionModel:
    # Initialize the ML model
    def __init__(self, ticker, sequence_length=60):
        self.ticker = ticker
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
    # Create sequences for LSTM model
    def _create_sequences(self, data):
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data[i:i + self.sequence_length])
            y.append(data[i + self.sequence_length])
        return np.array(X), np.array(y)
    
    # Build LSTM model architecture
    def _build_model(self, input_shape):
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50))
        model.add(Dropout(0.2))
        model.add(Dense(units=1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
    
    # Train the model on historical stock data
    def train(self, data, validation_split=0.2, epochs=50, batch_size=32):

        # Extract closing prices and scale
        closing_prices = data['close'].values.reshape(-1, 1)
        scaled_data = self.scaler.fit_transform(closing_prices)
        
        # Create sequences
        X, y = self._create_sequences(scaled_data)
        X = X.reshape(X.shape[0], X.shape[1], 1)
        
        # Build model
        self.model = self._build_model((X.shape[1], 1))
        
        # Define early stopping
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Train model
        self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[early_stopping],
            verbose=1
        )
        
        return self.model
    
    # Make predictions
    def predict(self, data, days_ahead=30):

        if self.model is None:
            raise ValueError("Model not trained or loaded. Call train() or load() first.")
        
        # Extract and scale closing prices
        closing_prices = data['close'].values.reshape(-1, 1)
        scaled_data = self.scaler.transform(closing_prices)
        
        # Create the most recent sequence for prediction
        last_sequence = scaled_data[-self.sequence_length:].reshape(1, self.sequence_length, 1)
        
        # Make predictions
        predictions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(days_ahead):
            # Predict next day
            next_day_scaled = self.model.predict(current_sequence)[0]
            predictions.append(next_day_scaled[0])
            
            # Update sequence for next prediction
            current_sequence = np.append(current_sequence[:, 1:, :], [[next_day_scaled]], axis=1)
        
        # Inverse transform to get actual prices
        predictions_array = np.array(predictions).reshape(-1, 1)
        predicted_prices = self.scaler.inverse_transform(predictions_array)
        
        return predicted_prices.flatten()
    
    # Save the trained model and scaler
    def save(self, filepath):

        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model
        self.model.save(filepath)
        
        # Save scaler
        scaler_path = filepath.replace('.h5', '_scaler.pkl')
        joblib.dump(self.scaler, scaler_path)
    
    # Load a trained model and scaler.
    def load(self, filepath):

        # Load model
        self.model = load_model(filepath)
        
        # Load scaler
        scaler_path = filepath.replace('.h5', '_scaler.pkl')
        self.scaler = joblib.load(scaler_path)