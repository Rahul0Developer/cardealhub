from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cars = db.relationship('Car', backref='owner', lazy='dynamic')
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic')
    liked_cars = db.relationship('LikedCar', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    kms_driven = db.Column(db.Integer, nullable=False)
    fuel_type = db.Column(db.String(20), nullable=False)
    transmission = db.Column(db.String(20))  # Manual or Automatic
    owners = db.Column(db.Integer, default=1)  # Number of previous owners
    color = db.Column(db.String(30))
    location = db.Column(db.String(100))  # City/location where car is available
    description = db.Column(db.Text)
    features = db.Column(db.Text)  # Car features as comma-separated list
    condition = db.Column(db.String(20))  # Excellent, Good, Fair, etc.
    
    # Seller contact info
    contact_name = db.Column(db.String(100))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    show_phone = db.Column(db.Boolean, default=True)  # Option to show/hide phone
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    image_path = db.Column(db.String(200))
    image_path2 = db.Column(db.String(200))  # Additional image
    image_path3 = db.Column(db.String(200))  # Additional image
    
    # Relationship with LikedCar
    liked_by = db.relationship('LikedCar', backref='car', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Car {self.name} - {self.year}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'company': self.company,
            'year': self.year,
            'price': self.price,
            'kms_driven': self.kms_driven,
            'fuel_type': self.fuel_type,
            'transmission': self.transmission,
            'owners': self.owners,
            'color': self.color,
            'location': self.location,
            'description': self.description,
            'features': self.features,
            'condition': self.condition,
            'contact_name': self.contact_name,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone if self.show_phone else None,
            'image_path': self.image_path,
            'image_path2': self.image_path2,
            'image_path3': self.image_path3,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    kms_driven = db.Column(db.Integer, nullable=False)
    fuel_type = db.Column(db.String(20), nullable=False)
    predicted_price = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Prediction {self.name} - {self.predicted_price}>'


class LikedCar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add a unique constraint to prevent duplicate likes
    __table_args__ = (db.UniqueConstraint('user_id', 'car_id', name='_user_car_uc'),)
    
    def __repr__(self):
        return f'<LikedCar User:{self.user_id} Car:{self.car_id}>'
        
        
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum('Success', 'Failed', 'Pending', name='transaction_status'), nullable=False, default='Pending')
    payment_method = db.Column(db.String(50), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True)  # For payment gateway reference
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    receipt_url = db.Column(db.String(255))
    
    # Relationships
    car = db.relationship('Car', backref=db.backref('transactions', lazy='dynamic'))
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref=db.backref('purchases', lazy='dynamic'))
    seller = db.relationship('User', foreign_keys=[seller_id], backref=db.backref('sales', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Transaction {self.id} - Car: {self.car_id}, Status: {self.status}>'
    
    def to_dict(self):
        """Convert transaction object to dictionary for API response"""
        return {
            'id': self.id,
            'car_id': self.car_id,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'amount': self.amount,
            'status': self.status,
            'payment_method': self.payment_method,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'transaction_id': self.transaction_id,
            'receipt_url': self.receipt_url
        }


class ListingStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False, unique=True)
    is_approved = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_sold = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    admin_notes = db.Column(db.Text)
    
    car = db.relationship('Car', backref=db.backref('status', uselist=False))
    
    def __repr__(self):
        return f'<ListingStatus Car:{self.car_id} Approved:{self.is_approved}>'
