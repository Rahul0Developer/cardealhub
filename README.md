# 🚗 Car Deal Hub - Intelligent Car Price Prediction & Marketplace

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Model Accuracy](https://img.shields.io/badge/R²_score-0.88-brightgreen.svg)]()

A comprehensive web application for car price prediction using machine learning, combined with a full-featured marketplace for buying and selling used cars.

## ✨ Features

### 🔮 ML-Powered Price Prediction
- **5 Advanced Models**: Linear Regression (Ridge), Random Forest, XGBoost, Gradient Boosting, Decision Tree
- **Optimized Hyperparameters**: Auto-tuned models using GridSearchCV and RandomizedSearchCV
- **High Accuracy**: Best model (XGBoost) achieves R² = 0.88
- **Real-time Predictions**: Get instant price estimates based on car specifications
- **Model Comparison**: Compare predictions across different algorithms

### 🛒 Complete Marketplace
- Browse and search used car listings
- Advanced filtering (brand, year, fuel type, price range)
- User authentication and authorization
- Car listing management (create, edit, delete)
- Admin approval system for listings
- Featured listings support

### 📊 Analytics Dashboard
- Price trends by brand and year
- Market analysis visualizations
- Historical price data charts
- Fuel type distribution analysis

### 💳 Transaction System
- Secure payment processing
- Transaction history tracking
- Digital receipt generation
- Buyer-seller connection

### 👥 User Features
- User registration and login
- Profile management
- Saved/favorite cars
- Prediction history
- Admin dashboard for moderators

## 🏗️ Project Structure

```
car-deal-hub/
├── app.py                 # Flask application configuration
├── main.py                # Application entry point
├── routes.py              # Main route handlers
├── admin_routes.py        # Admin-specific routes
├── user_routes.py         # User-specific routes
├── transaction_routes.py  # Payment and transaction handling
├── models.py              # SQLAlchemy database models
├── forms.py               # WTForm definitions
├── utils.py               # ML model training and utilities
├── db_migrate.py          # Database migration script
├── seed_cars.py           # Sample data seeder
├── reset_admin.py         # Admin password reset utility
│
├── data/
│   └── cleaned_data.csv   # Training dataset (816 records)
│
├── static/
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   ├── images/            # Static images
│   └── models/            # Trained ML models
│       ├── car_price_models.pkl    # All models (combined)
│       └── model_metrics.pkl       # Model performance metrics
│
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── predict.html
│   ├── marketplace.html
│   ├── trends.html
│   └── ...
│
├── tests/                 # Unit tests
│   ├── __init__.py
│   ├── test_utils.py      # ML model tests
│   └── test_app.py        # Application tests
│
├── sql_setup/             # SQL setup scripts
└── vscode_setup/          # VS Code configuration
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 14+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/car-deal-hub.git
   cd car-deal-hub
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   ```sql
   CREATE DATABASE cardealhub;
   ```

5. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/cardealhub
   SESSION_SECRET=your_secure_random_string
   SENDGRID_API_KEY=your_sendgrid_api_key (optional)
   ```

6. **Initialize database**
   ```bash
   python db_migrate.py
   python seed_cars.py  # Optional: load sample car listings
   ```

7. **Run the application**
   ```bash
   python main.py
   ```

8. **Access the application**
   
   Open your browser and navigate to: `http://localhost:5000`

## 🤖 Machine Learning Models

### Model Performance

| Model | MAE (₹) | RMSE (₹) | R² Score |
|-------|---------|----------|----------|
| **XGBoost** (Best) | 78,229 | 129,188 | **0.8802** |
| Ridge Regression | 90,979 | 151,700 | 0.8348 |
| Gradient Boosting | 93,449 | 159,127 | 0.8183 |
| Random Forest | 94,736 | 175,198 | 0.7797 |
| Decision Tree | 115,356 | 254,407 | 0.5354 |

### Features Used for Prediction
- **Company/Brand**: Car manufacturer (e.g., Maruti, Hyundai, Honda)
- **Model Name**: Specific car model
- **Year**: Manufacturing year
- **Kilometers Driven**: Odometer reading
- **Fuel Type**: Petrol, Diesel, or CNG

### Model Optimization
The models are trained with:
- **Data Preprocessing**: Outlier removal, LPG filtering
- **Feature Engineering**: One-hot encoding for categorical features, StandardScaler for numerical features
- **Hyperparameter Tuning**: 
  - GridSearchCV for linear models
  - RandomizedSearchCV for ensemble methods
- **Stratified Split**: Ensures balanced fuel type distribution in train/test sets

### Retraining Models

To retrain models with optimization:

```python
import pandas as pd
from utils import train_models

# Load data
df = pd.read_csv('data/cleaned_data.csv')

# Train with hyperparameter optimization
models = train_models(df, optimize=True)
```

To train without optimization (faster):

```python
models = train_models(df, optimize=False)
```

## 🧪 Running Tests

```bash
# Run all tests
python -m unittest discover -s tests -v

# Run specific test module
python -m unittest tests.test_utils -v
python -m unittest tests.test_app -v
```

## 📁 Database Schema

The application uses the following main tables:

- **User**: User accounts and authentication
- **Car**: Car listings with detailed specifications
- **Prediction**: History of price predictions
- **LikedCar**: User's favorite cars (many-to-many)
- **Transaction**: Purchase transactions
- **ListingStatus**: Admin approval and sale status

See [DATABASE-DESIGN.md](DATABASE-DESIGN.md) for complete schema documentation.

## 🎨 UI/UX Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern Interface**: Clean, intuitive navigation
- **Interactive Charts**: ECharts-powered visualizations
- **Real-time Validation**: Form validation with helpful feedback
- **Accessibility**: Semantic HTML and ARIA labels

## 🛠️ Technology Stack

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: ORM for database management
- **PostgreSQL**: Primary database
- **Scikit-learn**: Machine learning pipeline
- **XGBoost**: Gradient boosting library
- **Pandas**: Data manipulation

### Frontend
- **HTML5/CSS3**: Markup and styling
- **JavaScript**: Client-side interactivity
- **Bootstrap**: Responsive design framework
- **ECharts**: Data visualization

### DevOps
- **Gunicorn**: Production WSGI server
- **Git**: Version control
- **Unit Testing**: Built-in unittest framework

## 📝 API Endpoints

### Public Routes
- `GET /` - Home page
- `GET /marketplace` - Browse cars
- `GET /predict` - Price prediction form
- `POST /predict` - Get price prediction
- `GET /trends` - Market analytics

### User Routes (Authentication Required)
- `GET /list-car` - List a car for sale
- `POST /list-car` - Submit car listing
- `GET /my-listings` - View user's listings
- `GET /liked-cars` - View saved cars

### Admin Routes
- `GET /admin/dashboard` - Admin overview
- `GET /admin/listings` - Manage listings
- `POST /admin/approve/<id>` - Approve listing
- `POST /admin/reject/<id>` - Reject listing

## 🔐 Security Features

- Password hashing with Werkzeug
- CSRF protection
- SQL injection prevention (parameterized queries)
- Session management
- Role-based access control
- Input validation and sanitization

## 📊 Dataset

The model is trained on a curated dataset of 816 used car listings with the following characteristics:
- 25 unique car companies
- 254 different car models
- 3 fuel types (Petrol, Diesel, CNG)
- Price range: ₹50,000 - ₹5,000,000
- Year range: Various manufacturing years

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Car Deal Hub Team**

## 🙏 Acknowledgments

- Data sourced from public automotive datasets
- Built with open-source technologies
- Inspired by real-world car marketplace needs

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review the setup guide in README-SETUP.md

---

⭐ **Star this repo if you find it useful!**
