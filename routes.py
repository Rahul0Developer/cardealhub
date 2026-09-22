import os
import pandas as pd
import numpy as np
import pickle
import logging
import time
from flask import render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from models import User, Car, Prediction, LikedCar, ListingStatus, Transaction
from utils import predict_price, get_trend_data
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_routes(app, df, models=None):
    """
    Register all routes for the application
    
    Args:
        app: Flask application
        df: Pandas DataFrame with car data
        models: Dictionary of trained ML models
    """
    logger.info("Registering routes...")
    
    # Use the best model by default (XGBoost)
    model = models.get('xgboost') if models else None
    
    @app.route('/')
    def index():
        # Get trending cars (newest listings)
        trending_cars = Car.query.order_by(Car.created_at.desc()).limit(6).all()
        
        # Get popular brands
        popular_brands = df['company'].value_counts().head(6).to_dict()
        
        return render_template('index.html', trending_cars=trending_cars, popular_brands=popular_brands)
    
    @app.route('/marketplace')
    def marketplace():
        # Get filter parameters
        brand = request.args.get('brand', '')
        year = request.args.get('year', '')
        fuel_type = request.args.get('fuel_type', '')
        min_price = request.args.get('min_price', 0, type=int)
        max_price = request.args.get('max_price', 10000000, type=int)
        sort_by = request.args.get('sort_by', 'price')
        
        # Query cars with filters
        query = Car.query
        
        if brand and brand != 'All Brands':
            query = query.filter(Car.company == brand)
        if year and year != 'All Years':
            query = query.filter(Car.year == int(year))
        if fuel_type and fuel_type != 'All Types':
            query = query.filter(Car.fuel_type == fuel_type)
            
        query = query.filter(Car.price >= min_price, Car.price <= max_price)
        
        # Apply sorting
        if sort_by == 'price':
            query = query.order_by(Car.price)
        elif sort_by == 'year':
            query = query.order_by(Car.year.desc())
        elif sort_by == 'kms_driven':
            query = query.order_by(Car.kms_driven)
        
        cars = query.all()
        
        # Get unique brands, years, and fuel types for filters
        brands = df['company'].unique().tolist()
        years = sorted(df['year'].unique().tolist(), reverse=True)
        fuel_types = df['fuel_type'].unique().tolist()
        
        # Get list of liked car IDs for the current user
        liked_cars = []
        if current_user.is_authenticated:
            liked_cars = [like.car_id for like in current_user.liked_cars.all()]
        
        return render_template('marketplace.html', 
                               cars=cars, 
                               brands=brands, 
                               years=years, 
                               fuel_types=fuel_types,
                               liked_cars=liked_cars)
    
    @app.route('/predict', methods=['GET', 'POST'])
    def predict():
        if request.method == 'POST':
            # Get form data
            company = request.form.get('company')
            car_model = request.form.get('car_model')
            year = int(request.form.get('year'))
            kms_driven = int(request.form.get('kms_driven'))
            fuel_type = request.form.get('fuel_type')
            city = request.form.get('city')  # Optional
            
            # Use the models passed from main.py or empty dict if none
            all_models = models if models else {}
            
            # Check if models are available
            if not all_models:
                return jsonify({
                    'error': 'No trained models available',
                    'message': 'Please try again later'
                }), 500
            
            # Choose model (default to xgboost)
            model_type = request.form.get('model_type', 'xgboost')
            if model_type not in all_models:
                model_type = 'xgboost' if 'xgboost' in all_models else list(all_models.keys())[0]
            
            selected_model = all_models[model_type]
            
            # Predict price
            predicted_price = predict_price(
                selected_model, 
                company, 
                car_model, 
                year, 
                kms_driven, 
                fuel_type, 
                city
            )
            
            # Calculate price from other models for comparison
            model_predictions = {}
            for name, m in all_models.items():
                if name != model_type:
                    model_predictions[name] = predict_price(
                        m, company, car_model, year, kms_driven, fuel_type, city
                    )
            
            # Get historical price data for similar cars (for charts)
            similar_cars = df[
                (df['company'] == company) &
                (df['fuel_type'] == fuel_type)
            ]
            
            # Prepare chart data
            chart_data = {
                # Line chart: Year vs Price for similar cars
                'year_price': get_trend_data(similar_cars, 'year', 'Price', 'mean'),
                
                # Bar chart: Price by Models
                'model_price': get_trend_data(similar_cars, 'name', 'Price', 'mean'),
                
                # Scatter plot data: kms_driven vs Price
                'scatter_data': {
                    'x': similar_cars['kms_driven'].tolist(),
                    'y': similar_cars['Price'].tolist(),
                    'names': similar_cars['name'].tolist()
                }
            }
            
            # Save prediction to database if user is logged in
            user_id = session.get('user_id')
            if user_id:
                prediction = Prediction(
                    company=company,
                    name=car_model,
                    year=year,
                    kms_driven=kms_driven,
                    fuel_type=fuel_type,
                    predicted_price=predicted_price,
                    user_id=user_id
                )
                db.session.add(prediction)
                db.session.commit()
            
            # Return result with chart data
            return jsonify({
                'predicted_price': predicted_price,
                'model_predictions': model_predictions,
                'car_details': {
                    'company': company,
                    'model': car_model,
                    'year': year,
                    'kms_driven': kms_driven,
                    'fuel_type': fuel_type,
                    'city': city
                },
                'model_used': model_type,
                'chart_data': chart_data,
                'available_models': list(all_models.keys())
            })
        
        # GET request - render prediction form
        brands = sorted(df['company'].unique().tolist())
        years = sorted(df['year'].unique().tolist(), reverse=True)
        fuel_types = df['fuel_type'].unique().tolist()
        
        return render_template('predict.html', 
                               brands=brands, 
                               years=years, 
                               fuel_types=fuel_types)
    
    @app.route('/trends')
    def trends():
        # Get trend data
        price_by_brand = get_trend_data(df, 'company', 'Price', 'mean')
        price_by_year = get_trend_data(df, 'year', 'Price', 'mean')
        count_by_fuel = get_trend_data(df, 'fuel_type', 'name', 'count')
        price_by_fuel = get_trend_data(df, 'fuel_type', 'Price', 'mean')
        
        return render_template('trends.html',
                               price_by_brand=price_by_brand,
                               price_by_year=price_by_year,
                               count_by_fuel=count_by_fuel,
                               price_by_fuel=price_by_fuel)
    
    @app.route('/list-car', methods=['GET', 'POST'])
    @login_required
    def list_car():
        if request.method == 'POST':
            # Check if user is banned
            if current_user.is_banned:
                flash('Your account has been banned. You cannot list cars.', 'danger')
                return redirect(url_for('index'))
            
            try:
                # Get basic car data
                name = request.form.get('name')
                company = request.form.get('company')
                
                # Error handling for numeric fields
                try:
                    year = int(request.form.get('year'))
                except (ValueError, TypeError):
                    flash('Invalid year value', 'danger')
                    return redirect(url_for('list_car'))
                    
                try:
                    price = int(request.form.get('price'))
                except (ValueError, TypeError):
                    flash('Invalid price value', 'danger')
                    return redirect(url_for('list_car'))
                    
                try:
                    kms_driven = int(request.form.get('kms_driven'))
                except (ValueError, TypeError):
                    flash('Invalid kilometers value', 'danger')
                    return redirect(url_for('list_car'))
                
                fuel_type = request.form.get('fuel_type')
                description = request.form.get('description')
                
                # Get additional car details
                transmission = request.form.get('transmission')
                
                # Handle owners count safely
                try:
                    owners = int(request.form.get('owners', 1))
                except (ValueError, TypeError):
                    owners = 1
                    
                color = request.form.get('color')
                location = request.form.get('location')
                features = request.form.get('features')
                condition = request.form.get('condition')
                
                # Get contact information
                contact_name = request.form.get('contact_name', current_user.username)
                contact_email = request.form.get('contact_email', current_user.email)
                contact_phone = request.form.get('contact_phone')
                show_phone = 'show_phone' in request.form
                
                # Create image storage directory if it doesn't exist
                image_dir = os.path.join('static', 'images', 'cars')
                os.makedirs(image_dir, exist_ok=True)
                
                # Process primary image
                image_path = None
                if 'image' in request.files and request.files['image'].filename:
                    image = request.files['image']
                    image_filename = secure_filename(f"{current_user.id}_{company}_{name}_main_{int(time.time())}.jpg")
                    image_path = os.path.join('static/images/cars', image_filename)
                    image.save(image_path)
                
                # Process second image
                image_path2 = None
                if 'image2' in request.files and request.files['image2'].filename:
                    image2 = request.files['image2']
                    image_filename2 = secure_filename(f"{current_user.id}_{company}_{name}_2_{int(time.time())}.jpg")
                    image_path2 = os.path.join('static/images/cars', image_filename2)
                    image2.save(image_path2)
                    
                # Process third image
                image_path3 = None
                if 'image3' in request.files and request.files['image3'].filename:
                    image3 = request.files['image3']
                    image_filename3 = secure_filename(f"{current_user.id}_{company}_{name}_3_{int(time.time())}.jpg")
                    image_path3 = os.path.join('static/images/cars', image_filename3)
                    image3.save(image_path3)
                
                # Handle edit case
                edit_id = request.form.get('edit_id')
                if edit_id:
                    # Update existing car
                    car = Car.query.filter_by(id=edit_id, user_id=current_user.id).first()
                    if not car:
                        flash('Car not found or you do not have permission to edit it', 'danger')
                        return redirect(url_for('user.my_listings'))
                        
                    # Update fields
                    car.name = name
                    car.company = company
                    car.year = year
                    car.price = price
                    car.kms_driven = kms_driven
                    car.fuel_type = fuel_type
                    car.transmission = transmission
                    car.owners = owners
                    car.color = color
                    car.location = location
                    car.description = description
                    car.features = features
                    car.condition = condition
                    car.contact_name = contact_name
                    car.contact_email = contact_email
                    car.contact_phone = contact_phone
                    car.show_phone = show_phone
                    
                    # Only update image paths if new images were uploaded
                    if image_path:
                        car.image_path = image_path
                    if image_path2:
                        car.image_path2 = image_path2
                    if image_path3:
                        car.image_path3 = image_path3
                        
                    # Update timestamp
                    car.updated_at = datetime.utcnow()
                    
                    db.session.commit()
                    flash('Your car listing has been updated successfully!', 'success')
                else:
                    # Create new car listing with all data
                    car = Car(
                        name=name,
                        company=company,
                        year=year,
                        price=price,
                        kms_driven=kms_driven,
                        fuel_type=fuel_type,
                        transmission=transmission,
                        owners=owners,
                        color=color,
                        location=location,
                        description=description,
                        features=features,
                        condition=condition,
                        contact_name=contact_name,
                        contact_email=contact_email,
                        contact_phone=contact_phone,
                        show_phone=show_phone,
                        user_id=current_user.id,
                        image_path=image_path,
                        image_path2=image_path2,
                        image_path3=image_path3
                    )
                    
                    db.session.add(car)
                    db.session.commit()
                    
                    # Create a pending listing status
                    listing_status = ListingStatus(
                        car_id=car.id,
                        is_approved=False
                    )
                    db.session.add(listing_status)
                    db.session.commit()
                    
                    flash('Your car has been listed successfully! It will appear in the marketplace after admin approval.', 'success')
                
                return redirect(url_for('user.my_listings'))
                
            except Exception as e:
                db.session.rollback()
                import traceback
                print(traceback.format_exc())  # Detailed error for debugging
                flash('An error occurred while processing your request. Please try again.', 'danger')
                return redirect(url_for('list_car'))
        
        # GET request - render listing form
        brands = sorted(df['company'].unique().tolist())
        years = sorted(range(2000, 2025), reverse=True)  # Updated to include 2025
        fuel_types = df['fuel_type'].unique().tolist()
        
        # Check if editing an existing car
        edit_id = request.args.get('edit', type=int)
        car = None
        if edit_id:
            car = Car.query.filter_by(id=edit_id, user_id=current_user.id).first()
            if not car:
                flash('Car not found or you do not have permission to edit it', 'danger')
                return redirect(url_for('user.my_listings'))
        
        return render_template('list_car.html',
                               brands=brands,
                               years=years,
                               fuel_types=fuel_types,
                               car=car)
    
    @app.route('/contact')
    def contact():
        return render_template('contact.html')
        
    @app.route('/contact-seller/<int:car_id>')
    def contact_seller(car_id):
        # Get the car details
        car = Car.query.get_or_404(car_id)
        
        # Get similar cars (same brand, excluding current car)
        similar_cars = Car.query.filter(
            Car.company == car.company,
            Car.id != car.id
        ).order_by(Car.created_at.desc()).limit(3).all()
        
        # If we don't have enough similar cars from the same brand, get some based on price range
        if len(similar_cars) < 3:
            price_range_cars = Car.query.filter(
                Car.id != car.id,
                Car.company != car.company,  # Exclude cars we already have
                Car.price.between(car.price * 0.8, car.price * 1.2)  # Within 20% price range
            ).order_by(Car.created_at.desc()).limit(3 - len(similar_cars)).all()
            
            similar_cars.extend(price_range_cars)
        
        # Get list of liked car IDs for the current user
        liked_cars = []
        if current_user.is_authenticated:
            liked_cars = [like.car_id for like in current_user.liked_cars.all()]
            
        return render_template('contact_seller.html', 
                              car=car, 
                              similar_cars=similar_cars,
                              liked_cars=liked_cars)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Check if username or email already exists
            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                flash('Username or email already exists', 'error')
                return redirect(url_for('register'))
            
            # Create new user
            user = User(username=username, email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # Check if user is already logged in
        if current_user.is_authenticated:
            return redirect(url_for('index'))
            
        # Create login form
        from forms import LoginForm
        form = LoginForm()
        
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            remember = form.remember.data
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                # Update last login time
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                # Login the user with Flask-Login
                login_user(user, remember=remember)
                
                # Check if user is banned
                if user.is_banned:
                    flash('Your account has been banned. Please contact support.', 'danger')
                    logout_user()
                    return redirect(url_for('login'))
                
                flash('Logged in successfully!', 'success')
                
                # Redirect to requested page or index
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'danger')
        
        return render_template('login.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Logged out successfully!', 'success')
        return redirect(url_for('index'))
    
    @app.route('/api/car-models', methods=['GET'])
    def get_car_models():
        brand = request.args.get('brand', '')
        if not brand:
            return jsonify([])
        
        # Get car models for the selected brand
        car_models = df[df['company'] == brand]['name'].unique().tolist()
        return jsonify(car_models)
    
    # Resource pages
    @app.route('/blog')
    def blog():
        return render_template('blog.html')
        
    @app.route('/car-buying-guide')
    def car_buying_guide():
        return render_template('car_buying_guide.html')
        
    @app.route('/car-selling-tips')
    def car_selling_tips():
        return render_template('car_selling_tips.html')
        
    @app.route('/faq')
    def faq():
        return render_template('faq.html')
    
    # Redirect all 404 and 500 errors to homepage
    @app.errorhandler(404)
    def page_not_found(e):
        flash('The page you were looking for does not exist. You have been redirected to the homepage.', 'info')
        return redirect(url_for('index'))
    
    @app.errorhandler(500)
    def server_error(e):
        flash('Sorry, an internal server error occurred. You have been redirected to the homepage.', 'warning')
        return redirect(url_for('index'))
