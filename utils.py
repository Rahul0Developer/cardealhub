import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import pickle
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_models(df, optimize=False):
    """Train multiple car price prediction models using the provided dataset
    
    Args:
        df: Pandas DataFrame with car data
        optimize: Boolean flag to enable hyperparameter optimization (default: False)
    
    Returns:
        Dictionary of trained models
    """
    
    # Store models in a dictionary
    models = {}
    model_metrics = {}
    
    # Define model directories
    models_dir = os.path.join(os.path.dirname(__file__), 'static', 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Define combined model path (one file for all models)
    combined_model_path = os.path.join(models_dir, 'car_price_models.pkl')
    metrics_path = os.path.join(models_dir, 'model_metrics.pkl')
    
    # Always try to load existing models first
    if os.path.exists(combined_model_path):
        try:
            with open(combined_model_path, 'rb') as f:
                models = pickle.load(f)
            logger.info(f"Loaded existing combined models with {len(models)} models")
            
            # Return early if all required models were loaded successfully
            required_models = ['linear', 'random_forest', 'xgboost', 'gradient_boosting', 'decision_tree']
            if all(model in models for model in required_models):
                return models
            
        except Exception as e:
            logger.error(f"Error loading combined models: {e}")
    
    # Prepare data for training (only if we need to train)
    # Remove any rows with LPG as fuel_type
    df = df[df['fuel_type'] != 'LPG'].copy()
    
    # Additional data cleaning
    # Remove outliers - prices that are too low or too high
    df = df[(df['Price'] > 50000) & (df['Price'] < 5000000)]
    
    # Remove cars with extremely high mileage (potential outliers)
    df = df[df['kms_driven'] < 500000]
    
    # Prepare features and target
    X = df[['company', 'name', 'year', 'kms_driven', 'fuel_type']]
    y = df['Price']
    
    # Split data into training and testing sets with stratification on fuel_type
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=df['fuel_type']
    )
    
    logger.info(f"Training data size: {len(X_train)}, Test data size: {len(X_test)}")
    
    # Define the preprocessing for categorical features
    categorical_features = ['company', 'name', 'fuel_type']
    numerical_features = ['year', 'kms_driven']
    
    # Use OneHotEncoder for categorical features with better handling
    categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    
    # Add scaler for numerical features
    numerical_transformer = StandardScaler()
    
    # Create a preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', categorical_transformer, categorical_features),
            ('num', numerical_transformer, numerical_features)
        ],
        remainder='drop'
    )
    
    logger.info("Starting model training..." if not optimize else "Starting model training with optimization...")
    
    # Create and train model pipelines
    
    # 1. Ridge Regression (better than Linear Regression for multicollinearity)
    if 'linear' not in models:
        logger.info("Training Ridge Regression model...")
        ridge_model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', Ridge(alpha=1.0))
        ])
        ridge_model.fit(X_train, y_train)
        
        models['linear'] = ridge_model
        logger.info("Trained Ridge Regression model")
    
    # 2. Random Forest
    if 'random_forest' not in models:
        logger.info("Training Random Forest model...")
        rf_model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', RandomForestRegressor(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1))
        ])
        rf_model.fit(X_train, y_train)
        
        models['random_forest'] = rf_model
        logger.info("Trained Random Forest model")
    
    # 3. XGBoost
    if 'xgboost' not in models:
        logger.info("Training XGBoost model...")
        xgb_model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', xgb.XGBRegressor(objective='reg:squarederror', n_estimators=300, 
                                          max_depth=5, learning_rate=0.05, random_state=42, n_jobs=-1))
        ])
        xgb_model.fit(X_train, y_train)
        
        models['xgboost'] = xgb_model
        logger.info("Trained XGBoost model")
    
    # 4. Gradient Boosting Regression
    if 'gradient_boosting' not in models:
        logger.info("Training Gradient Boosting model...")
        gb_model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', GradientBoostingRegressor(n_estimators=200, max_depth=5, 
                                                   learning_rate=0.05, random_state=42))
        ])
        gb_model.fit(X_train, y_train)
        
        models['gradient_boosting'] = gb_model
        logger.info("Trained Gradient Boosting model")
    
    # 5. Decision Tree Regression
    if 'decision_tree' not in models:
        logger.info("Training Decision Tree model...")
        dt_model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', DecisionTreeRegressor(max_depth=10, random_state=42))
        ])
        dt_model.fit(X_train, y_train)
        
        models['decision_tree'] = dt_model
        logger.info("Trained Decision Tree model")
    
    # Evaluate all models and store metrics
    logger.info("\n" + "="*60)
    logger.info("MODEL EVALUATION RESULTS")
    logger.info("="*60)
    
    best_model_name = None
    best_r2 = -float('inf')
    
    for name, model in models.items():
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        model_metrics[name] = {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'r2': r2
        }
        
        logger.info(f"{name:20s} - MAE: ₹{mae:,.2f}, RMSE: ₹{rmse:,.2f}, R²: {r2:.4f}")
        
        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name
    
    logger.info("="*60)
    logger.info(f"Best performing model: {best_model_name} with R² = {best_r2:.4f}")
    logger.info("="*60 + "\n")
    
    # Save all models in a single file
    with open(combined_model_path, 'wb') as f:
        pickle.dump(models, f)
    logger.info(f"Saved combined models with {len(models)} models to {combined_model_path}")
    
    # Save model metrics
    with open(metrics_path, 'wb') as f:
        pickle.dump(model_metrics, f)
    logger.info(f"Saved model metrics to {metrics_path}")
    
    return models

def train_model(df):
    """Train and return the default model (for backward compatibility)"""
    models = train_models(df)
    # Return the best model (XGBoost by default)
    return models.get('xgboost', models['linear'])

def predict_price(model, company, model_name, year, kms_driven, fuel_type, city=None):
    """Predict car price using the trained model"""
    
    # Create input data for prediction
    input_data = pd.DataFrame({
        'company': [company],
        'name': [model_name],
        'year': [year],
        'kms_driven': [kms_driven],
        'fuel_type': [fuel_type]
    })
    
    # Make prediction
    try:
        predicted_price = model.predict(input_data)[0]
        
        # Round to nearest thousand for nicer display
        predicted_price = round(predicted_price / 1000) * 1000
        
        # Ensure the predicted price is not negative
        predicted_price = max(predicted_price, 50000)
        
        return int(predicted_price)
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return 0

def get_trend_data(df, group_by, value_col, agg_func):
    """Generate trend data for visualizations"""
    
    if agg_func == 'mean':
        result = df.groupby(group_by)[value_col].mean().reset_index()
    elif agg_func == 'median':
        result = df.groupby(group_by)[value_col].median().reset_index()
    elif agg_func == 'count':
        result = df.groupby(group_by)[value_col].count().reset_index()
    else:
        result = df.groupby(group_by)[value_col].sum().reset_index()
    
    # Convert to list format for ECharts
    categories = result[group_by].tolist()
    values = result[value_col].tolist()
    
    # Round values if they are prices
    if value_col == 'price' or value_col == 'Price':
        values = [round(val / 1000) * 1000 for val in values]
    
    return {
        'categories': categories,
        'values': values
    }
