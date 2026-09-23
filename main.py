import os
import pandas as pd
import logging
from app import app
from utils import train_models
from routes import register_routes
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Current year for templates
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Load data
data_path = os.path.join(os.path.dirname(__file__), 'data', 'cleaned_data.csv')
attached_data_path = os.path.join(os.path.dirname(__file__), 'attached_assets', 'Cleaned_data.csv')

# Try to load the data from different locations
if os.path.exists(data_path):
    df = pd.read_csv(data_path)
    logger.info(f"Loaded data from {data_path}")
elif os.path.exists(attached_data_path):
    df = pd.read_csv(attached_data_path)
    logger.info(f"Loaded data from {attached_data_path}")
else:
    raise FileNotFoundError("Could not find the cleaned_data.csv file")

# Filter out LPG fuel type
df = df[df['fuel_type'] != 'LPG']
logger.info(f"Loaded data with {len(df)} rows after filtering out LPG")

# Train models (with optimize=False to load existing models if available)
models = train_models(df, optimize=False)
logger.info(f"Trained {len(models)} models")

# Register routes
register_routes(app, df, models)

# Register transaction routes blueprint
from transaction_routes import transaction_bp
app.register_blueprint(transaction_bp, url_prefix='/transaction')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
