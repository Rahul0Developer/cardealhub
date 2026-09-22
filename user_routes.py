from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app import db
from models import User, Car, Prediction, LikedCar, Transaction, ListingStatus
from sqlalchemy import func
from datetime import datetime

user_bp = Blueprint('user', __name__, url_prefix='/user')

# Check if user is banned
def check_banned():
    if current_user.is_banned:
        flash('Your account has been banned. Please contact support for more information.', 'danger')
        return redirect(url_for('index'))
    return None

# User Dashboard
@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Check if user is banned
    banned_redirect = check_banned()
    if banned_redirect:
        return banned_redirect
    
    # Get user stats
    cars_count = Car.query.filter_by(user_id=current_user.id).count()
    predictions_count = Prediction.query.filter_by(user_id=current_user.id).count()
    liked_cars_count = LikedCar.query.filter_by(user_id=current_user.id).count()
    
    # Get transaction count (either as buyer or seller)
    transactions_count = Transaction.query.filter(
        (Transaction.buyer_id == current_user.id) | 
        (Transaction.seller_id == current_user.id)
    ).count()
    
    # Recent activity
    recent_cars = Car.query.filter_by(user_id=current_user.id).order_by(Car.created_at.desc()).limit(3).all()
    recent_predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).limit(3).all()
    
    # Recent transactions (both buying and selling)
    recent_transactions = Transaction.query.filter(
        (Transaction.buyer_id == current_user.id) | 
        (Transaction.seller_id == current_user.id)
    ).order_by(Transaction.timestamp.desc()).limit(3).all()
    
    # Car status
    car_status = db.session.query(
        Car, func.count(LikedCar.id).label('likes_count')
    ).outerjoin(LikedCar, Car.id == LikedCar.car_id).filter(
        Car.user_id == current_user.id
    ).group_by(Car.id).order_by(Car.created_at.desc()).limit(5).all()
    
    return render_template(
        'user/dashboard.html',
        cars_count=cars_count,
        predictions_count=predictions_count,
        liked_cars_count=liked_cars_count,
        transactions_count=transactions_count,
        recent_cars=recent_cars,
        recent_predictions=recent_predictions,
        recent_transactions=recent_transactions,
        car_status=car_status,
        user=current_user
    )

# User's car listings
@user_bp.route('/my-listings')
@login_required
def my_listings():
    # Check if user is banned
    banned_redirect = check_banned()
    if banned_redirect:
        return banned_redirect
    
    page = request.args.get('page', 1, type=int)
    
    # Get user's car listings with like counts
    listings = db.session.query(
        Car, func.count(LikedCar.id).label('likes_count')
    ).outerjoin(LikedCar, Car.id == LikedCar.car_id).filter(
        Car.user_id == current_user.id
    ).group_by(Car.id).order_by(Car.created_at.desc())
    
    # Paginate results
    pagination = listings.paginate(page=page, per_page=10, error_out=False)
    
    return render_template(
        'user/my_listings.html',
        pagination=pagination
    )

# User's prediction history
@user_bp.route('/prediction-history')
@login_required
def prediction_history():
    # Check if user is banned
    banned_redirect = check_banned()
    if banned_redirect:
        return banned_redirect
    
    page = request.args.get('page', 1, type=int)
    
    # Get user's prediction history
    predictions = Prediction.query.filter_by(
        user_id=current_user.id
    ).order_by(Prediction.created_at.desc())
    
    # Paginate results
    pagination = predictions.paginate(page=page, per_page=10, error_out=False)
    
    return render_template(
        'user/prediction_history.html',
        pagination=pagination
    )

# User's liked cars
@user_bp.route('/liked-cars')
@login_required
def liked_cars():
    # Check if user is banned
    banned_redirect = check_banned()
    if banned_redirect:
        return banned_redirect
    
    page = request.args.get('page', 1, type=int)
    
    # Get user's liked cars
    liked = db.session.query(Car).join(
        LikedCar, Car.id == LikedCar.car_id
    ).filter(LikedCar.user_id == current_user.id).order_by(LikedCar.created_at.desc())
    
    # Paginate results
    pagination = liked.paginate(page=page, per_page=10, error_out=False)
    
    return render_template(
        'user/liked_cars.html',
        pagination=pagination
    )

# Like/unlike a car
@user_bp.route('/like/<int:car_id>', methods=['POST'])
@login_required
def toggle_like(car_id):
    # Check if user is banned
    if current_user.is_banned:
        return jsonify({'success': False, 'message': 'Your account has been banned'}), 403
    
    car = Car.query.get_or_404(car_id)
    
    # Check if already liked
    existing_like = LikedCar.query.filter_by(
        user_id=current_user.id, car_id=car_id
    ).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        action = 'unliked'
    else:
        # Like
        like = LikedCar(user_id=current_user.id, car_id=car_id)
        db.session.add(like)
        action = 'liked'
    
    db.session.commit()
    
    # Get updated like count
    likes_count = LikedCar.query.filter_by(car_id=car_id).count()
    
    return jsonify({
        'success': True,
        'action': action,
        'likes_count': likes_count
    })

# Delete car listing
@user_bp.route('/my-listings/delete/<int:car_id>', methods=['POST'])
@login_required
def delete_car(car_id):
    # Check if user is banned
    banned_redirect = check_banned()
    if banned_redirect:
        return banned_redirect
    
    # Find the car
    car = Car.query.get_or_404(car_id)
    
    # Check if user owns the car
    if car.user_id != current_user.id:
        flash('You do not have permission to delete this listing', 'danger')
        return redirect(url_for('user.my_listings'))
    
    try:
        # Instead of using nested transaction which can cause issues,
        # delete related data one by one
        
        # First, delete any likes for this car
        likes = LikedCar.query.filter_by(car_id=car_id).all()
        for like in likes:
            db.session.delete(like)
        
        # Delete all transactions for this car if any
        transactions = Transaction.query.filter_by(car_id=car_id).all()
        for transaction in transactions:
            db.session.delete(transaction)
        
        # Delete listing status if exists
        listing_status = ListingStatus.query.filter_by(car_id=car_id).first()
        if listing_status:
            db.session.delete(listing_status)
        
        # Finally, delete the car
        db.session.delete(car)
        
        # Commit all deletions
        db.session.commit()
        
        flash('Your car listing has been successfully deleted', 'success')
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        import traceback
        print(traceback.format_exc())  # Print detailed error for debugging
        flash(f'An error occurred while deleting the listing', 'danger')
    
    return redirect(url_for('user.my_listings'))

# User profile settings
@user_bp.route('/profile')
@login_required
def profile():
    # Check if user is banned
    banned_redirect = check_banned()
    if banned_redirect:
        return banned_redirect
    
    return render_template('user/profile.html', user=current_user)

# Update user profile
@user_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    # Check if user is banned
    if current_user.is_banned:
        flash('Your account has been banned. Please contact support for more information.', 'danger')
        return redirect(url_for('index'))
    
    # Get form data
    username = request.form.get('username')
    email = request.form.get('email')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Update username and email if provided
    if username and username != current_user.username:
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Username already exists', 'danger')
            return redirect(url_for('user.profile'))
        
        current_user.username = username
    
    if email and email != current_user.email:
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Email already exists', 'danger')
            return redirect(url_for('user.profile'))
        
        current_user.email = email
    
    # Update password if provided
    if current_password and new_password and confirm_password:
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('user.profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('user.profile'))
        
        current_user.set_password(new_password)
    
    db.session.commit()
    flash('Profile updated successfully', 'success')
    return redirect(url_for('user.profile'))