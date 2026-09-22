"""
Unit tests for Flask application routes and database models
"""
import unittest
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAppConfiguration(unittest.TestCase):
    """Test cases for Flask app configuration"""
    
    def test_app_exists(self):
        """Test that Flask app is properly configured"""
        from app import app
        self.assertIsNotNone(app)
        self.assertEqual(app.name, 'app')
    
    def test_secret_key_exists(self):
        """Test that secret key is configured"""
        from app import app
        self.assertIsNotNone(app.secret_key)
    
    def test_database_uri_configured(self):
        """Test that database URI is configured"""
        from app import app
        self.assertIn('SQLALCHEMY_DATABASE_URI', app.config)


class TestModels(unittest.TestCase):
    """Test cases for database models"""
    
    def test_user_model_imports(self):
        """Test that User model can be imported"""
        from models import User
        self.assertIsNotNone(User)
    
    def test_car_model_imports(self):
        """Test that Car model can be imported"""
        from models import Car
        self.assertIsNotNone(Car)
    
    def test_prediction_model_imports(self):
        """Test that Prediction model can be imported"""
        from models import Prediction
        self.assertIsNotNone(Prediction)
    
    def test_likedcar_model_imports(self):
        """Test that LikedCar model can be imported"""
        from models import LikedCar
        self.assertIsNotNone(LikedCar)


class TestDataLoading(unittest.TestCase):
    """Test cases for data loading functionality"""
    
    def test_data_file_exists(self):
        """Test that cleaned data file exists"""
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cleaned_data.csv')
        self.assertTrue(os.path.exists(data_path), "cleaned_data.csv not found")
    
    def test_data_loads_correctly(self):
        """Test that data loads without errors"""
        import pandas as pd
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cleaned_data.csv')
        df = pd.read_csv(data_path)
        
        self.assertGreater(len(df), 0, "Data file is empty")
        self.assertIn('Price', df.columns, "Price column missing")
        self.assertIn('company', df.columns, "company column missing")
        self.assertIn('fuel_type', df.columns, "fuel_type column missing")


class TestModelFiles(unittest.TestCase):
    """Test cases for trained model files"""
    
    def test_model_file_exists(self):
        """Test that trained model file exists"""
        model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'static', 'models', 'car_price_models.pkl'
        )
        self.assertTrue(os.path.exists(model_path), "Trained model file not found. Run training first.")
    
    def test_model_file_not_empty(self):
        """Test that model file is not empty"""
        import pickle
        model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'static', 'models', 'car_price_models.pkl'
        )
        
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                models = pickle.load(f)
            
            self.assertGreater(len(models), 0, "No models found in model file")
            
            # Check all required models exist
            required_models = ['linear', 'random_forest', 'xgboost', 'gradient_boosting', 'decision_tree']
            for model_name in required_models:
                self.assertIn(model_name, models, f"{model_name} model not found")


if __name__ == '__main__':
    unittest.main()
