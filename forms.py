from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, FileField, HiddenField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class PredictionForm(FlaskForm):
    company = SelectField('Brand', validators=[DataRequired()])
    car_model = SelectField('Model', validators=[DataRequired()])
    year = SelectField('Year', validators=[DataRequired()], coerce=int)
    kms_driven = IntegerField('Kilometers Driven', validators=[DataRequired(), NumberRange(min=0)])
    fuel_type = SelectField('Fuel Type', validators=[DataRequired()])
    city = StringField('City', validators=[Optional()])
    model_type = SelectField('Select Model Type', validators=[Optional()])
    submit = SubmitField('Predict Price')

class CarListingForm(FlaskForm):
    name = StringField('Car Model', validators=[DataRequired(), Length(max=100)])
    company = SelectField('Brand', validators=[DataRequired()])
    year = SelectField('Year', validators=[DataRequired()], coerce=int)
    price = IntegerField('Price (₹)', validators=[DataRequired(), NumberRange(min=0)])
    kms_driven = IntegerField('Kilometers Driven', validators=[DataRequired(), NumberRange(min=0)])
    fuel_type = SelectField('Fuel Type', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    image = FileField('Car Image', validators=[Optional()])
    submit = SubmitField('Submit Listing')

class UserProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', 
                                    validators=[Optional(), EqualTo('new_password')])
    submit = SubmitField('Update Profile')
    
class PaymentMethodForm(FlaskForm):
    """Form to select payment method"""
    PAYMENT_METHODS = [
        ('credit_card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('wallet', 'Digital Wallet')
    ]
    payment_method = RadioField('Payment Method', choices=PAYMENT_METHODS, validators=[DataRequired()])
    cardholder_name = StringField('Cardholder Name', validators=[Optional(), Length(max=64)])
    card_number = StringField('Card Number', validators=[Optional(), Length(min=16, max=16)])
    expiry_date = StringField('Expiry Date (MM/YY)', validators=[Optional(), Length(min=5, max=5)])
    cvv = StringField('CVV', validators=[Optional(), Length(min=3, max=4)])
    upi_id = StringField('UPI ID', validators=[Optional(), Length(max=50)])
    wallet_id = StringField('Wallet Username/ID', validators=[Optional(), Length(max=50)])
    agree_terms = BooleanField('I agree to the terms and conditions', validators=[DataRequired()])
    submit = SubmitField('Make Payment')