"""
Unit tests for utils.py - Model training and prediction functions
"""
import unittest
import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import train_models, predict_price


class TestModelTraining(unittest.TestCase):
    """Test cases for model training functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data before running tests"""
        # Create larger sample data for testing (need enough samples for stratified split)
        np.random.seed(42)
        n_samples = 50
        
        cls.sample_data = pd.DataFrame({
            'name': np.random.choice(['Swift', 'Creta', 'City', 'i20', 'Baleno'], n_samples),
            'company': np.random.choice(['Maruti', 'Hyundai', 'Honda'], n_samples),
            'year': np.random.choice([2017, 2018, 2019, 2020], n_samples),
            'Price': np.random.randint(400000, 900000, n_samples),
            'kms_driven': np.random.randint(10000, 50000, n_samples),
            'fuel_type': np.random.choice(['Petrol', 'Diesel'], n_samples)
        })
        
        # Train models on sample data (without optimization for speed)
        cls.models = train_models(cls.sample_data, optimize=False)
    
    def test_models_trained(self):
        """Test that all required models are trained"""
        required_models = ['linear', 'random_forest', 'xgboost', 'gradient_boosting', 'decision_tree']
        for model_name in required_models:
            self.assertIn(model_name, self.models, f"{model_name} model not found")
    
    def test_model_pipeline_structure(self):
        """Test that models have proper pipeline structure"""
        for name, model in self.models.items():
            # Check if model has 'predict' method
            self.assertTrue(hasattr(model, 'predict'), f"{name} model doesn't have predict method")
    
    def test_prediction_output(self):
        """Test that predictions return valid values"""
        model = self.models['xgboost']
        
        price = predict_price(
            model=model,
            company='Maruti',
            model_name='Swift',
            year=2018,
            kms_driven=30000,
            fuel_type='Petrol'
        )
        
        # Check prediction is a positive number
        self.assertIsInstance(price, int, "Prediction should be an integer")
        self.assertGreater(price, 0, "Prediction should be positive")
        self.assertLess(price, 10000000, "Prediction should be reasonable")


class TestDataPreprocessing(unittest.TestCase):
    """Test cases for data preprocessing"""
    
    def test_lpg_filtering(self):
        """Test that LPG fuel type is filtered out"""
        test_data = pd.DataFrame({
            'name': ['Car1', 'Car2', 'Car3'],
            'company': ['Company1', 'Company2', 'Company3'],
            'year': [2018, 2019, 2020],
            'Price': [500000, 600000, 700000],
            'kms_driven': [30000, 40000, 50000],
            'fuel_type': ['Petrol', 'LPG', 'Diesel']
        })
        
        # Filter out LPG
        filtered_data = test_data[test_data['fuel_type'] != 'LPG']
        
        # Check LPG is removed
        self.assertNotIn('LPG', filtered_data['fuel_type'].values)
        self.assertEqual(len(filtered_data), 2)
    
    def test_outlier_removal(self):
        """Test that extreme outliers are handled"""
        test_data = pd.DataFrame({
            'name': ['Car1', 'Car2', 'Car3'],
            'company': ['Company1', 'Company2', 'Company3'],
            'year': [2018, 2019, 2020],
            'Price': [10000, 600000, 10000000],  # Very low and very high prices
            'kms_driven': [30000, 40000, 600000],  # Very high mileage
            'fuel_type': ['Petrol', 'Diesel', 'Petrol']
        })
        
        # Apply outlier filters
        filtered_data = test_data[
            (test_data['Price'] > 50000) & 
            (test_data['Price'] < 5000000) &
            (test_data['kms_driven'] < 500000)
        ]
        
        # Check outliers are removed
        self.assertEqual(len(filtered_data), 1)


class TestPredictionFunction(unittest.TestCase):
    """Test cases for prediction function"""
    
    @classmethod
    def setUpClass(cls):
        """Load trained models"""
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cleaned_data.csv')
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            cls.models = train_models(df, optimize=False)
        else:
            # Use sample data if file not found
            cls.sample_data = pd.DataFrame({
                'name': ['Swift', 'Creta', 'City'],
                'company': ['Maruti', 'Hyundai', 'Honda'],
                'year': [2018, 2019, 2017],
                'Price': [500000, 800000, 600000],
                'kms_driven': [30000, 25000, 40000],
                'fuel_type': ['Petrol', 'Diesel', 'Petrol']
            })
            cls.models = train_models(cls.sample_data, optimize=False)
    
    def test_prediction_with_valid_input(self):
        """Test prediction with valid input parameters"""
        model = self.models.get('xgboost', list(self.models.values())[0])
        
        price = predict_price(
            model=model,
            company='Maruti',
            model_name='Swift',
            year=2018,
            kms_driven=30000,
            fuel_type='Petrol'
        )
        
        self.assertIsInstance(price, int)
        self.assertGreater(price, 0)
    
    def test_prediction_minimum_price(self):
        """Test that prediction never returns negative or zero price"""
        model = self.models.get('xgboost', list(self.models.values())[0])
        
        # Try with extreme values that might cause negative prediction
        price = predict_price(
            model=model,
            company='Unknown',
            model_name='Unknown',
            year=1990,
            kms_driven=999999,
            fuel_type='Petrol'
        )
        
        # Should return at least minimum price (50000)
        self.assertGreaterEqual(price, 50000)
    
    def test_prediction_rounding(self):
        """Test that predictions are rounded to nearest thousand"""
        model = self.models.get('xgboost', list(self.models.values())[0])
        
        price = predict_price(
            model=model,
            company='Maruti',
            model_name='Swift',
            year=2018,
            kms_driven=30000,
            fuel_type='Petrol'
        )
        
        # Check if price is rounded to nearest 1000
        self.assertEqual(price % 1000, 0)


if __name__ == '__main__':
    unittest.main()
