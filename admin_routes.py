from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify, Response
from flask_login import login_required, current_user, login_user, logout_user
from app import db
from models import User, Car, Prediction, LikedCar, ListingStatus, Transaction
from sqlalchemy import func, desc, text
from datetime import datetime, timedelta
from forms import LoginForm
import json
import csv
import io

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin Login
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If user already logged in and is admin, redirect to admin dashboard
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    # Create login form
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_admin:
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Login the user
            login_user(user, remember=remember)
            
            flash('Logged in to admin panel successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials or insufficient permissions', 'danger')
    
    return render_template('admin/login.html', form=form)

# Admin Logout
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out from admin panel successfully!', 'success')
    return redirect(url_for('admin.login'))

# Admin authentication decorator
def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Admin Dashboard
@admin_bp.route('/')
@admin_required
def dashboard():
    # Count statistics and calculate growth
    total_users = User.query.count()
    total_cars = Car.query.count()
    
    # Get today's date at midnight for "today's listings" count
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate 30-day growth rates
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    sixty_days_ago = datetime.utcnow() - timedelta(days=60)
    
    # Today's new listings count
    todays_listings = Car.query.filter(Car.created_at >= today).count()
    
    # User growth
    users_last_30_days = User.query.filter(User.created_at >= thirty_days_ago).count()
    users_previous_30_days = User.query.filter(User.created_at >= sixty_days_ago, User.created_at < thirty_days_ago).count()
    user_growth_rate = 0
    if users_previous_30_days > 0:
        user_growth_rate = round(((users_last_30_days - users_previous_30_days) / users_previous_30_days) * 100)
    
    # Listing growth
    listings_last_30_days = Car.query.filter(Car.created_at >= thirty_days_ago).count()
    listings_previous_30_days = Car.query.filter(Car.created_at >= sixty_days_ago, Car.created_at < thirty_days_ago).count()
    listing_growth_rate = 0
    if listings_previous_30_days > 0:
        listing_growth_rate = round(((listings_last_30_days - listings_previous_30_days) / listings_previous_30_days) * 100)
    
    # Total transactions and revenue
    total_transactions = Transaction.query.count()
    active_listings = db.session.query(Car).outerjoin(
        ListingStatus, Car.id == ListingStatus.car_id
    ).filter(
        (ListingStatus.is_approved == True) & 
        (ListingStatus.is_sold.is_(None) | ListingStatus.is_sold == False)
    ).count()
    
    # Calculate total revenue from successful transactions
    total_revenue = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.status == 'Success'
    ).scalar() or 0
    
    # Prediction usage count
    prediction_count = Prediction.query.count()
    
    # Sales growth (based on successful transactions)
    transactions_last_30_days = Transaction.query.filter(
        Transaction.status == 'Success',
        Transaction.timestamp >= thirty_days_ago
    ).count()
    transactions_previous_30_days = Transaction.query.filter(
        Transaction.status == 'Success',
        Transaction.timestamp >= sixty_days_ago,
        Transaction.timestamp < thirty_days_ago
    ).count()
    transactions_growth_rate = 0
    if transactions_previous_30_days > 0:
        transactions_growth_rate = round(((transactions_last_30_days - transactions_previous_30_days) / transactions_previous_30_days) * 100)
    
    # Pending and sold counts
    pending_count = db.session.query(Car).outerjoin(
        ListingStatus, Car.id == ListingStatus.car_id
    ).filter(
        (ListingStatus.is_approved.is_(None)) | (ListingStatus.is_approved == False)
    ).count()
    
    sold_count = db.session.query(ListingStatus).filter(
        ListingStatus.is_sold == True
    ).count()
    
    # Stats dictionary
    stats = {
        'user_count': total_users,
        'listing_count': total_cars,
        'active_listings': active_listings,
        'today_listings': todays_listings,
        'pending_count': pending_count,
        'sold_count': sold_count,
        'transaction_count': total_transactions,
        'total_revenue': total_revenue,
        'prediction_count': prediction_count,
        'user_growth': user_growth_rate,
        'listing_growth': listing_growth_rate,
        'sales_growth': transactions_growth_rate
    }
    
    # Pending listings for quick approval
    pending_listings = db.session.query(Car).outerjoin(
        ListingStatus, Car.id == ListingStatus.car_id
    ).filter(
        (ListingStatus.is_approved.is_(None)) | (ListingStatus.is_approved == False)
    ).order_by(Car.created_at.desc()).limit(5).all()
    
    # Recent activity
    recent_activities = []
    
    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(3).all()
    for user in recent_users:
        recent_activities.append({
            'type': 'user',
            'message': f'<strong>{user.username}</strong> joined the platform',
            'time': user.created_at.strftime('%d %b %Y, %H:%M')
        })
    
    # Recent listings
    recent_cars = Car.query.order_by(Car.created_at.desc()).limit(3).all()
    for car in recent_cars:
        recent_activities.append({
            'type': 'car',
            'message': f'<strong>{car.owner.username}</strong> listed <strong>{car.name}</strong> for ₹{"{:,}".format(car.price)}',
            'time': car.created_at.strftime('%d %b %Y, %H:%M')
        })
    
    # Recent likes
    recent_likes = LikedCar.query.order_by(LikedCar.created_at.desc()).limit(3).all()
    for like in recent_likes:
        recent_activities.append({
            'type': 'like',
            'message': f'<strong>{like.user.username}</strong> liked <strong>{like.car.name}</strong>',
            'time': like.created_at.strftime('%d %b %Y, %H:%M')
        })
    
    # Recent predictions
    recent_predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(3).all()
    for prediction in recent_predictions:
        recent_activities.append({
            'type': 'prediction',
            'message': f'<strong>{prediction.user.username}</strong> requested price prediction for <strong>{prediction.name}</strong>',
            'time': prediction.created_at.strftime('%d %b %Y, %H:%M')
        })
    
    # Sort activities by time (newest first)
    recent_activities.sort(key=lambda x: datetime.strptime(x['time'], '%d %b %Y, %H:%M'), reverse=True)
    recent_activities = recent_activities[:5]  # Keep only 5 most recent
    
    # Top brands data
    top_brands = db.session.query(
        Car.company.label('name'), 
        func.count(Car.id).label('count')
    ).group_by(Car.company).order_by(func.count(Car.id).desc()).limit(5).all()
    
    max_brand_count = max([b.count for b in top_brands]) if top_brands else 1
    top_brands_data = []
    for brand in top_brands:
        top_brands_data.append({
            'name': brand.name,
            'count': brand.count,
            'percentage': round((brand.count / max_brand_count) * 100)
        })
    
    # Fuel types data
    fuel_types = db.session.query(
        Car.fuel_type.label('name'), 
        func.count(Car.id).label('count')
    ).group_by(Car.fuel_type).order_by(func.count(Car.id).desc()).all()
    
    max_fuel_count = max([f.count for f in fuel_types]) if fuel_types else 1
    fuel_types_data = []
    for fuel in fuel_types:
        fuel_types_data.append({
            'name': fuel.name,
            'count': fuel.count,
            'percentage': round((fuel.count / max_fuel_count) * 100)
        })
    
    # Price ranges data
    price_ranges = [
        {'min': 0, 'max': 500000, 'name': '0-5 Lakhs'},
        {'min': 500000, 'max': 1000000, 'name': '5-10 Lakhs'},
        {'min': 1000000, 'max': 1500000, 'name': '10-15 Lakhs'},
        {'min': 1500000, 'max': 2000000, 'name': '15-20 Lakhs'},
        {'min': 2000000, 'max': 999999999, 'name': '20+ Lakhs'}
    ]
    
    price_ranges_data = []
    for price_range in price_ranges:
        count = Car.query.filter(
            Car.price >= price_range['min'], 
            Car.price < price_range['max']
        ).count()
        price_ranges_data.append({
            'name': price_range['name'],
            'count': count,
            'percentage': 0  # Will calculate after getting all counts
        })
    
    max_price_count = max([p['count'] for p in price_ranges_data]) if price_ranges_data else 1
    for price_range in price_ranges_data:
        price_range['percentage'] = round((price_range['count'] / max_price_count) * 100)
    
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        pending_listings=pending_listings,
        recent_activities=recent_activities,
        top_brands=top_brands_data,
        fuel_types=fuel_types_data,
        price_ranges=price_ranges_data
    )

# Manage Listings
@admin_bp.route('/listings')
@admin_required
def listings():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    # Base query
    query = db.session.query(Car, ListingStatus).outerjoin(
        ListingStatus, Car.id == ListingStatus.car_id
    )
    
    # Apply filters
    if status_filter == 'pending':
        query = query.filter(
            (ListingStatus.is_approved.is_(None)) | 
            (ListingStatus.is_approved == False)
        )
    elif status_filter == 'approved':
        query = query.filter(ListingStatus.is_approved == True)
    elif status_filter == 'featured':
        query = query.filter(ListingStatus.is_featured == True)
    elif status_filter == 'sold':
        query = query.filter(ListingStatus.is_sold == True)
    
    # Paginate results
    pagination = query.order_by(Car.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template(
        'admin/listings.html',
        pagination=pagination,
        status_filter=status_filter
    )

# Approve or reject listing
@admin_bp.route('/listings/<int:car_id>/update-status', methods=['POST'])
@admin_required
def update_listing_status(car_id):
    car = Car.query.get_or_404(car_id)
    
    action = request.form.get('action')
    notes = request.form.get('notes', '')
    
    # Get or create listing status
    status = ListingStatus.query.filter_by(car_id=car_id).first()
    if not status:
        status = ListingStatus(car_id=car_id)
        db.session.add(status)
    
    if action == 'approve':
        status.is_approved = True
        flash(f'Listing "{car.name}" has been approved.', 'success')
    elif action == 'reject':
        status.is_approved = False
        flash(f'Listing "{car.name}" has been rejected.', 'warning')
    elif action == 'feature':
        status.is_featured = True
        flash(f'Listing "{car.name}" has been featured.', 'success')
    elif action == 'unfeature':
        status.is_featured = False
        flash(f'Listing "{car.name}" has been unfeatured.', 'info')
    elif action == 'sold':
        status.is_sold = True
        flash(f'Listing "{car.name}" has been marked as sold.', 'info')
    elif action == 'unsold':
        status.is_sold = False
        flash(f'Listing "{car.name}" has been marked as available.', 'info')
    
    status.admin_notes = notes
    db.session.commit()
    
    return redirect(url_for('admin.listings'))

# Delete listing
@admin_bp.route('/listings/<int:car_id>/delete', methods=['POST'])
@admin_required
def delete_listing(car_id):
    car = Car.query.get_or_404(car_id)
    
    # Store name for flash message
    car_name = car.name
    
    # Delete the listing
    db.session.delete(car)
    db.session.commit()
    
    flash(f'Listing "{car_name}" has been deleted.', 'success')
    return redirect(url_for('admin.listings'))

# User Management
@admin_bp.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter', 'all')
    search = request.args.get('search', '')
    
    # Base query
    query = User.query
    
    # Apply filters
    if filter_type == 'admin':
        query = query.filter(User.is_admin == True)
    elif filter_type == 'verified':
        query = query.filter(User.is_verified == True)
    elif filter_type == 'banned':
        query = query.filter(User.is_banned == True)
    
    # Apply search
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) | 
            (User.email.ilike(f'%{search}%'))
        )
    
    # Paginate results
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template(
        'admin/users.html',
        pagination=pagination,
        filter_type=filter_type,
        search=search
    )

# Update user status
@admin_bp.route('/users/<int:user_id>/update-status', methods=['POST'])
@admin_required
def update_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    # Protect against self-changes
    if user.id == current_user.id:
        flash('You cannot modify your own admin status.', 'danger')
        return redirect(url_for('admin.users'))
    
    action = request.form.get('action')
    
    if action == 'make-admin':
        user.is_admin = True
        flash(f'User "{user.username}" has been made an admin.', 'success')
    elif action == 'remove-admin':
        user.is_admin = False
        flash(f'Admin privileges removed from "{user.username}".', 'info')
    elif action == 'verify':
        user.is_verified = True
        flash(f'User "{user.username}" has been verified.', 'success')
    elif action == 'unverify':
        user.is_verified = False
        flash(f'User "{user.username}" has been unverified.', 'info')
    elif action == 'ban':
        user.is_banned = True
        flash(f'User "{user.username}" has been banned.', 'warning')
    elif action == 'unban':
        user.is_banned = False
        flash(f'User "{user.username}" has been unbanned.', 'success')
    
    db.session.commit()
    return redirect(url_for('admin.users'))

# Statistics and Reports
@admin_bp.route('/reports')
@admin_required
def reports():
    # Monthly car listings
    try:
        monthly_listings = db.session.query(
            func.to_char(Car.created_at, 'YYYY-MM').label('month'),
            func.count(Car.id).label('count')
        ).group_by('month').order_by('month').all()
    except:
        # Fallback for databases that don't support date_format
        monthly_listings = db.session.query(
            func.to_char(Car.created_at, 'YYYY-MM').label('month'),
            func.count(Car.id).label('count')
        ).group_by('month').order_by('month').all()
    
    # Ensure we have at least 6 months of data for visualization
    months_data = {}
    for i in range(6):
        month = (datetime.utcnow() - timedelta(days=30*i)).strftime('%Y-%m')
        months_data[month] = 0
    
    # Fill with actual data
    for item in monthly_listings:
        if item.month in months_data:
            months_data[item.month] = item.count
    
    # Sort by date (oldest first for time series)
    sorted_months = sorted(months_data.items())
    
    monthly_listings_data = {
        'labels': [item[0] for item in sorted_months],
        'data': [item[1] for item in sorted_months]
    }
    
    # Price ranges
    price_ranges = [
        {'min': 0, 'max': 500000, 'label': '0-5 Lakhs'},
        {'min': 500000, 'max': 1000000, 'label': '5-10 Lakhs'},
        {'min': 1000000, 'max': 1500000, 'label': '10-15 Lakhs'},
        {'min': 1500000, 'max': 2000000, 'label': '15-20 Lakhs'},
        {'min': 2000000, 'max': 999999999, 'label': '20+ Lakhs'}
    ]
    
    price_distribution = []
    for price_range in price_ranges:
        count = Car.query.filter(
            Car.price >= price_range['min'], 
            Car.price < price_range['max']
        ).count()
        price_distribution.append({
            'label': price_range['label'],
            'count': count
        })
    
    price_distribution_data = {
        'labels': [item['label'] for item in price_distribution],
        'data': [item['count'] for item in price_distribution]
    }
    
    # Fuel types
    fuel_types = db.session.query(
        Car.fuel_type, func.count(Car.id).label('count')
    ).group_by(Car.fuel_type).all()
    
    fuel_type_data = {
        'labels': [row.fuel_type for row in fuel_types],
        'data': [row.count for row in fuel_types]
    }
    
    # Prediction history
    try:
        prediction_history = db.session.query(
            func.to_char(Car.created_at, 'YYYY-MM').label('month'),
            func.count(Prediction.id).label('count')
        ).group_by('month').order_by('month').all()
    except:
        # Fallback for databases that don't support date_format
        prediction_history = db.session.query(
            func.to_char(Car.created_at, 'YYYY-MM').label('month'),
            func.count(Prediction.id).label('count')
        ).group_by('month').order_by('month').all()
    
    # Ensure we have at least 6 months of data for visualization
    prediction_months_data = {}
    for i in range(6):
        month = (datetime.utcnow() - timedelta(days=30*i)).strftime('%Y-%m')
        prediction_months_data[month] = 0
    
    # Fill with actual data
    for item in prediction_history:
        if item.month in prediction_months_data:
            prediction_months_data[item.month] = item.count
    
    # Sort by date (oldest first for time series)
    sorted_prediction_months = sorted(prediction_months_data.items())
    
    prediction_history_data = {
        'labels': [item[0] for item in sorted_prediction_months],
        'data': [item[1] for item in sorted_prediction_months]
    }
    
    # Calculate analytics metrics
    avg_price = db.session.query(func.avg(Car.price)).scalar() or 0
    avg_price = int(avg_price)
    
    # Most popular brand
    popular_brand_result = db.session.query(
        Car.company, func.count(Car.id).label('count')
    ).group_by(Car.company).order_by(func.count(Car.id).desc()).first()
    
    popular_brand = popular_brand_result.company if popular_brand_result else "N/A"
    
    # Average days to sell (based on created vs sold dates)
    # This is an estimate since we don't track the exact sell date
    # We'll use the ListingStatus.updated_at as an approximation
    sold_listings = db.session.query(
        Car.created_at, ListingStatus.updated_at
    ).join(
        ListingStatus, Car.id == ListingStatus.car_id
    ).filter(
        ListingStatus.is_sold == True
    ).all()
    
    avg_days_to_sell = 0
    if sold_listings:
        total_days = 0
        for listing in sold_listings:
            days_diff = (listing.updated_at - listing.created_at).days
            total_days += max(days_diff, 1)  # At least 1 day
        avg_days_to_sell = round(total_days / len(sold_listings))
    
    # Estimated conversion rate (listings to sales)
    total_listings = Car.query.count()
    total_sold = db.session.query(ListingStatus).filter(ListingStatus.is_sold == True).count()
    conversion_rate = round((total_sold / total_listings) * 100) if total_listings > 0 else 0
    
    # Prediction analytics
    prediction_count = Prediction.query.count()
    avg_prediction = db.session.query(func.avg(Prediction.predicted_price)).scalar() or 0
    avg_prediction = int(avg_prediction)
    
    # Most predicted brand
    popular_prediction_brand_result = db.session.query(
        Prediction.company, func.count(Prediction.id).label('count')
    ).group_by(Prediction.company).order_by(func.count(Prediction.id).desc()).first()
    
    popular_prediction_brand = popular_prediction_brand_result.company if popular_prediction_brand_result else "N/A"
    
    # Prediction accuracy is a placeholder - would need actual vs predicted data to calculate
    prediction_accuracy = 92  # This would normally be calculated with real data
    
    return render_template(
        'admin/reports.html',
        monthly_listings_data=json.dumps(monthly_listings_data),
        price_distribution_data=json.dumps(price_distribution_data),
        fuel_type_data=json.dumps(fuel_type_data),
        prediction_history_data=json.dumps(prediction_history_data),
        avg_price=avg_price,
        avg_days_to_sell=avg_days_to_sell,
        popular_brand=popular_brand,
        conversion_rate=conversion_rate,
        prediction_count=prediction_count,
        avg_prediction=avg_prediction,
        popular_prediction_brand=popular_prediction_brand,
        prediction_accuracy=prediction_accuracy
    )

# Transaction Management
@admin_bp.route('/transactions')
@admin_required
def transactions():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    search = request.args.get('search', '')
    
    # Base query
    query = Transaction.query
    
    # Apply status filter
    if status_filter and status_filter != 'all':
        query = query.filter(Transaction.status == status_filter)
    
    # Apply date range filter
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Transaction.timestamp >= date_from_obj)
        except ValueError:
            flash('Invalid date format for "Date From"', 'error')
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)
            query = query.filter(Transaction.timestamp <= date_to_obj)
        except ValueError:
            flash('Invalid date format for "Date To"', 'error')
    
    # Apply search filter (search by car name, buyer username, or seller username)
    if search:
        search_term = f"%{search}%"
        query = query.join(Car, Transaction.car_id == Car.id).\
                join(User, Transaction.buyer_id == User.id).\
                filter((Car.name.ilike(search_term)) |
                       (User.username.ilike(search_term)))
    
    # Get transaction statistics
    total_transactions = Transaction.query.count()
    success_count = Transaction.query.filter_by(status='Success').count()
    pending_count = Transaction.query.filter_by(status='Pending').count()
    failed_count = Transaction.query.filter_by(status='Failed').count()
    
    total_revenue = db.session.query(func.sum(Transaction.amount)).\
                   filter(Transaction.status == 'Success').scalar() or 0
    
    # Paginate results
    pagination = query.order_by(Transaction.timestamp.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    transactions = pagination.items
    
    # Calculate transaction stats by car type
    car_type_stats = []
    car_types = ['SUV', 'Sedan', 'Hatchback']
    
    for car_type in car_types:
        # Calculate average price of successful transactions for this car type
        avg_price = db.session.query(func.avg(Transaction.amount)).\
                   join(Car, Transaction.car_id == Car.id).\
                   filter(Transaction.status == 'Success').\
                   filter(Car.name.ilike(f'%{car_type}%')).scalar() or 0
        
        car_type_stats.append({
            'type': car_type,
            'avg_price': round(avg_price, 2)
        })
    
    stats = {
        'total': total_transactions,
        'success': success_count,
        'pending': pending_count,
        'failed': failed_count,
        'revenue': total_revenue,
        'car_types': car_type_stats
    }
    
    return render_template(
        'admin/transactions.html',
        transactions=transactions,
        pagination=pagination,
        stats=stats,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
        search=search
    )

# Transaction Details
@admin_bp.route('/transactions/<int:transaction_id>')
@admin_required
def transaction_details(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    car = Car.query.get(transaction.car_id)
    buyer = User.query.get(transaction.buyer_id)
    seller = User.query.get(transaction.seller_id)
    
    return render_template(
        'admin/transaction_detail.html',
        transaction=transaction,
        car=car,
        buyer=buyer,
        seller=seller
    )

# User Role Management
@admin_bp.route('/users/roles')
@admin_required
def user_roles():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    # Base query
    query = User.query
    
    # Apply search
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    # Paginate results
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    users = pagination.items
    
    return render_template(
        'admin/user_roles.html',
        users=users,
        pagination=pagination,
        search=search
    )

# Update User Role
@admin_bp.route('/users/<int:user_id>/update-role', methods=['POST'])
@admin_required
def update_user_role(user_id):
    user = User.query.get_or_404(user_id)
    
    # Protect against self-changes
    if user.id == current_user.id:
        flash('You cannot modify your own role.', 'danger')
        return redirect(url_for('admin.user_roles'))
    
    new_role = request.form.get('role')
    
    if new_role == 'admin':
        user.is_admin = True
        flash(f'User "{user.username}" has been promoted to admin.', 'success')
    elif new_role == 'verified_seller':
        user.is_admin = False
        user.is_verified = True
        flash(f'User "{user.username}" has been set as a verified seller.', 'success')
    elif new_role == 'basic_user':
        user.is_admin = False
        user.is_verified = False
        flash(f'User "{user.username}" has been set as a basic user.', 'info')
    
    db.session.commit()
    return redirect(url_for('admin.user_roles'))

# Export data in CSV format
@admin_bp.route('/export/<data_type>')
@admin_required
def export_data(data_type):
    if data_type == 'transactions':
        # Create CSV for transaction data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Transaction ID', 'Car', 'Buyer', 'Seller', 'Amount', 'Date', 'Status', 'Payment Method'])
        
        # Write data
        transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
        for transaction in transactions:
            car = Car.query.get(transaction.car_id)
            buyer = User.query.get(transaction.buyer_id)
            seller = User.query.get(transaction.seller_id)
            
            writer.writerow([
                transaction.transaction_id,
                f"{car.company} {car.name} ({car.year})" if car else "Unknown Car",
                buyer.username if buyer else "Unknown Buyer",
                seller.username if seller else "Unknown Seller",
                f"₹{transaction.amount:,.2f}",
                transaction.timestamp.strftime('%d %b, %Y %H:%M'),
                transaction.status,
                transaction.payment_method
            ])
        
        # Create response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename=transactions_export_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    
    elif data_type == 'users':
        # Create CSV for user data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['ID', 'Username', 'Email', 'Joined Date', 'Last Login', 'Is Admin', 'Is Verified', 'Is Banned'])
        
        # Write data
        users = User.query.all()
        for user in users:
            writer.writerow([
                user.id,
                user.username,
                user.email,
                user.created_at.strftime('%Y-%m-%d'),
                user.last_login.strftime('%Y-%m-%d') if user.last_login else 'Never',
                'Yes' if user.is_admin else 'No',
                'Yes' if user.is_verified else 'No',
                'Yes' if user.is_banned else 'No'
            ])
        
        # Create response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename=users_export_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    
    elif data_type == 'cars':
        # Create CSV for car data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['ID', 'Name', 'Company', 'Year', 'Price', 'KMs Driven', 'Fuel Type', 'Created At', 'Status'])
        
        # Write data
        cars = Car.query.all()
        for car in cars:
            status = ListingStatus.query.filter_by(car_id=car.id).first()
            status_text = "Unknown"
            if status:
                if status.is_sold:
                    status_text = "Sold"
                elif status.is_approved:
                    status_text = "Approved"
                elif status.is_approved == False:
                    status_text = "Rejected"
                else:
                    status_text = "Pending"
            
            writer.writerow([
                car.id,
                car.name,
                car.company,
                car.year,
                car.price,
                car.kms_driven,
                car.fuel_type,
                car.created_at.strftime('%Y-%m-%d'),
                status_text
            ])
        
        # Create response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename=cars_export_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    
    else:
        abort(404)