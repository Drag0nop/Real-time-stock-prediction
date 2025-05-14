# Replace with your actual API key to Polygon.io API Key

POLYGON_API_KEY = "YOUR_POLYGON_API_KEY"

# Model configuration
SEQUENCE_LENGTH = 60  # Number of days to use for prediction input
PREDICTION_DAYS = [1, 5, 15, 30]  # Available prediction days for frontend
DEFAULT_STOCK = "AAPL"  # Default stock ticker

# Flask application settings
DEBUG = True
SECRET_KEY = "your-secret-key-here"  # Change this to a random string in production