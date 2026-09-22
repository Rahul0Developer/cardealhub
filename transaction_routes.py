import os
import uuid
import logging
import sys
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, abort
from flask_login import login_required, current_user
from app import db
from models import Car, User, Transaction, ListingStatus
from forms import PaymentMethodForm
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import random  # For simulating payment processing

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/payment/<int:car_id>', methods=['GET', 'POST'])
@login_required
def payment_page(car_id):
    """Display payment form for a car"""
    # Get the car details
    car = Car.query.get_or_404(car_id)
    
    # Check if the car is available for purchase
    listing_status = ListingStatus.query.filter_by(car_id=car.id).first()
    if not listing_status or not listing_status.is_approved or listing_status.is_sold:
        flash('This car is not available for purchase.', 'error')
        return redirect(url_for('marketplace'))
    
    # Check if user is trying to buy their own car
    if car.user_id == current_user.id:
        flash('You cannot purchase your own car.', 'error')
        return redirect(url_for('marketplace'))
    
    # Calculate processing fee (2% of car price)
    processing_fee = car.price * 0.02
    total_amount = car.price + processing_fee
    
    form = PaymentMethodForm()
    
    if form.validate_on_submit():
        try:
            # Process the payment (simulated)
            payment_successful, transaction_id = process_payment(
                car_id=car.id,
                buyer_id=current_user.id,
                seller_id=car.user_id,
                amount=total_amount,
                payment_method=form.payment_method.data
            )
            
            if payment_successful:
                flash('Payment successful! Your transaction is complete.', 'success')
                return redirect(url_for('transaction.payment_success', transaction_id=transaction_id))
            else:
                flash('Payment failed. Please try again.', 'error')
                return redirect(url_for('transaction.payment_failure', car_id=car.id))
        except Exception as e:
            logging.error(f"Payment error: {str(e)}")
            flash('An error occurred during payment processing. Please try again later.', 'error')
            return redirect(url_for('transaction.payment_failure', car_id=car.id))
    
    return render_template('payment.html', car=car, form=form, 
                          processing_fee=processing_fee, total_amount=total_amount)

@transaction_bp.route('/payment/process/<int:car_id>', methods=['POST'])
@login_required
def payment_process(car_id):
    """Process payment for a car (POST only)"""
    if request.method != 'POST':
        abort(405)  # Method Not Allowed
    
    car = Car.query.get_or_404(car_id)
    form = PaymentMethodForm()
    
    if form.validate_on_submit():
        try:
            # Calculate total amount
            processing_fee = car.price * 0.02
            total_amount = car.price + processing_fee
            
            # Process the payment (simulated)
            payment_successful, transaction_id = process_payment(
                car_id=car.id,
                buyer_id=current_user.id,
                seller_id=car.user_id,
                amount=total_amount,
                payment_method=form.payment_method.data
            )
            
            if payment_successful:
                return redirect(url_for('transaction.payment_success', transaction_id=transaction_id))
            else:
                return redirect(url_for('transaction.payment_failure', car_id=car.id))
        except Exception as e:
            logging.error(f"Payment error: {str(e)}")
            flash('An error occurred during payment processing. Please try again later.', 'error')
            return redirect(url_for('transaction.payment_failure', car_id=car.id))
    
    # If form validation fails
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{field}: {error}", 'error')
    
    return redirect(url_for('transaction.payment_page', car_id=car.id))

@transaction_bp.route('/payment/success/<int:transaction_id>')
@login_required
def payment_success(transaction_id):
    """Display payment success page"""
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Ensure the user is the buyer
    if transaction.buyer_id != current_user.id and not current_user.is_admin:
        abort(403)  # Forbidden
    
    return render_template('payment_success.html', transaction=transaction)

@transaction_bp.route('/payment/failure/<int:car_id>')
@login_required
def payment_failure(car_id):
    """Display payment failure page"""
    car = Car.query.get_or_404(car_id)
    error_message = request.args.get('error', 'Your payment could not be processed. Please try again.')
    
    return render_template('payment_failure.html', car_id=car.id, error_message=error_message)

@transaction_bp.route('/payment/check-status/<int:transaction_id>')
@login_required
def check_payment_status(transaction_id):
    """Check the status of a pending payment"""
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Ensure the user is the buyer or seller
    if transaction.buyer_id != current_user.id and transaction.seller_id != current_user.id and not current_user.is_admin:
        abort(403)  # Forbidden
    
    # In a real implementation, this would check with the payment gateway
    # Here we'll simply update the transaction status randomly for demonstration
    if transaction.status == 'Pending':
        # 80% chance of success for demo purposes
        if random.random() < 0.8:
            transaction.status = 'Success'
            
            # Mark car as sold
            listing_status = ListingStatus.query.filter_by(car_id=transaction.car_id).first()
            if listing_status:
                listing_status.is_sold = True
                db.session.commit()
            
            # Send success email notification
            try:
                send_transaction_email(transaction.id, 'success')
            except Exception as e:
                logging.error(f"Failed to send success email: {str(e)}")
            
            flash('Payment has been successfully processed!', 'success')
            return redirect(url_for('transaction.payment_success', transaction_id=transaction.id))
        else:
            transaction.status = 'Failed'
            db.session.commit()
            
            # Send failed email notification
            try:
                send_transaction_email(transaction.id, 'failed')
            except Exception as e:
                logging.error(f"Failed to send failure email: {str(e)}")
            
            flash('Payment processing failed. Please try again.', 'error')
            return redirect(url_for('transaction.payment_failure', car_id=transaction.car_id))
    
    # If already processed, redirect appropriately
    if transaction.status == 'Success':
        return redirect(url_for('transaction.payment_success', transaction_id=transaction.id))
    else:
        return redirect(url_for('transaction.payment_failure', car_id=transaction.car_id))

@transaction_bp.route('/transactions/history')
@login_required
def transactions_history():
    """View transaction history for the current user"""
    transaction_type = request.args.get('type', 'purchases')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if transaction_type == 'purchases':
        # Show purchases (user is buyer)
        transactions = Transaction.query.filter_by(buyer_id=current_user.id)
    else:
        # Show sales (user is seller)
        transactions = Transaction.query.filter_by(seller_id=current_user.id)
    
    # Order by most recent first
    transactions = transactions.order_by(Transaction.timestamp.desc())
    
    # Paginate results
    pagination = transactions.paginate(page=page, per_page=per_page, error_out=False)
    transactions = pagination.items
    
    return render_template('transactions.html', 
                          transactions=transactions, 
                          pagination=pagination,
                          transaction_type=transaction_type)

def process_payment(car_id, buyer_id, seller_id, amount, payment_method):
    """
    Simulate payment processing
    Returns (success_bool, transaction_id_or_error_message)
    """
    try:
        # Generate a unique transaction ID
        transaction_id = str(uuid.uuid4())
        
        # Create a new transaction record with Pending status
        transaction = Transaction(
            car_id=car_id,
            buyer_id=buyer_id,
            seller_id=seller_id,
            amount=amount,
            status='Pending',  # Initially pending
            payment_method=payment_method,
            transaction_id=transaction_id,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Simulate payment processing delay and randomness
        # In a real app, this would call a payment gateway API
        
        # Simulate success (90% of the time for demo)
        if random.random() < 0.9:
            # Update transaction status to success
            transaction.status = 'Success'
            
            # Mark car as sold
            listing_status = ListingStatus.query.filter_by(car_id=car_id).first()
            if listing_status:
                listing_status.is_sold = True
            
            db.session.commit()
            
            # Generate a receipt URL (simulated)
            transaction.receipt_url = url_for('transaction.generate_receipt', transaction_id=transaction.id, _external=True)
            db.session.commit()
            
            # Send success email notifications
            try:
                send_transaction_email(transaction.id, 'success')
            except Exception as e:
                logging.error(f"Failed to send success email: {str(e)}")
            
            return True, transaction.id
        else:
            # Update transaction status to failed
            transaction.status = 'Failed'
            db.session.commit()
            
            # Send failed email notification
            try:
                send_transaction_email(transaction.id, 'failed')
            except Exception as e:
                logging.error(f"Failed to send failure email: {str(e)}")
            
            return False, transaction.id
    
    except Exception as e:
        logging.error(f"Payment processing error: {str(e)}")
        db.session.rollback()
        raise

@transaction_bp.route('/transaction/receipt/<int:transaction_id>')
@login_required
def generate_receipt(transaction_id):
    """Generate receipt for a transaction"""
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Ensure the user is authorized to view this receipt
    if transaction.buyer_id != current_user.id and transaction.seller_id != current_user.id and not current_user.is_admin:
        abort(403)  # Forbidden
    
    # Only successful transactions have receipts
    if transaction.status != 'Success':
        flash('Receipt is only available for successful transactions.', 'error')
        return redirect(url_for('transaction.transactions_history'))
    
    # In a real implementation, this would generate a PDF receipt
    # For now, we'll just show a receipt page
    return render_template('receipt.html', transaction=transaction)

# Blueprint is registered in main.py

def send_transaction_email(transaction_id, notification_type):
    """
    Send transaction email notifications
    
    Args:
        transaction_id (int): ID of the transaction
        notification_type (str): Type of notification ('success', 'pending', 'failed')
    """
    # Make sure we have SendGrid API key
    sendgrid_key = os.environ.get('SENDGRID_API_KEY')
    if not sendgrid_key:
        logging.warning("SendGrid API key not found. Email notifications disabled.")
        return False
        
    try:
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            logging.error(f"Transaction {transaction_id} not found")
            return False
            
        buyer = User.query.get(transaction.buyer_id)
        seller = User.query.get(transaction.seller_id)
        car = Car.query.get(transaction.car_id)
        
        # Default sender email
        from_email = "notifications@cardealhub.com"
        
        # Configure email based on notification type
        if notification_type == 'success':
            # Email to buyer
            buyer_subject = f"Your Car Purchase Is Complete - {car.company} {car.name}"
            buyer_html = f"""
            <h2>Congratulations on your new car purchase!</h2>
            <p>Dear {buyer.username},</p>
            <p>Your payment of ₹{transaction.amount:,.2f} for the {car.year} {car.company} {car.name} has been successfully processed.</p>
            <p>Transaction ID: {transaction.transaction_id}</p>
            <p>Purchase Date: {transaction.timestamp.strftime('%d %b %Y')}</p>
            <p>You can view your receipt and transaction details in your <a href="http://cardealhub.com/transaction/receipt/{transaction.id}">account dashboard</a>.</p>
            <p>The seller will contact you shortly regarding delivery details.</p>
            <p>Thank you for using Car Deal Hub!</p>
            """
            
            buyer_message = Mail(
                from_email=Email(from_email),
                to_emails=To(buyer.email),
                subject=buyer_subject,
                html_content=Content("text/html", buyer_html)
            )
            
            # Email to seller
            seller_subject = f"Your Car Has Been Sold - {car.company} {car.name}"
            seller_html = f"""
            <h2>Your car has been sold!</h2>
            <p>Dear {seller.username},</p>
            <p>Great news! Your {car.year} {car.company} {car.name} has been purchased by {buyer.username} for ₹{transaction.amount:,.2f}.</p>
            <p>Transaction ID: {transaction.transaction_id}</p>
            <p>Sale Date: {transaction.timestamp.strftime('%d %b %Y')}</p>
            <p>Please coordinate with the buyer for delivery arrangements. You can view transaction details in your <a href="http://cardealhub.com/transaction/receipt/{transaction.id}">account dashboard</a>.</p>
            <p>Thank you for using Car Deal Hub!</p>
            """
            
            seller_message = Mail(
                from_email=Email(from_email),
                to_emails=To(seller.email),
                subject=seller_subject,
                html_content=Content("text/html", seller_html)
            )
            
            # Send emails
            sg = SendGridAPIClient(sendgrid_key)
            sg.send(buyer_message)
            sg.send(seller_message)
            
            logging.info(f"Transaction success emails sent for transaction {transaction_id}")
            return True
            
        elif notification_type == 'pending':
            # Only notify buyer for pending transactions
            buyer_subject = f"Your Car Purchase Is Being Processed - {car.company} {car.name}"
            buyer_html = f"""
            <h2>Your payment is being processed</h2>
            <p>Dear {buyer.username},</p>
            <p>We have received your payment request of ₹{transaction.amount:,.2f} for the {car.year} {car.company} {car.name}.</p>
            <p>Transaction ID: {transaction.transaction_id}</p>
            <p>Your payment is currently being processed. We'll notify you once it's complete.</p>
            <p>You can check the status in your <a href="http://cardealhub.com/transaction/history">transaction history</a>.</p>
            <p>Thank you for using Car Deal Hub!</p>
            """
            
            buyer_message = Mail(
                from_email=Email(from_email),
                to_emails=To(buyer.email),
                subject=buyer_subject,
                html_content=Content("text/html", buyer_html)
            )
            
            # Send email
            sg = SendGridAPIClient(sendgrid_key)
            sg.send(buyer_message)
            
            logging.info(f"Transaction pending email sent for transaction {transaction_id}")
            return True
            
        elif notification_type == 'failed':
            # Only notify buyer for failed transactions
            buyer_subject = f"Your Car Purchase Payment Failed - {car.company} {car.name}"
            buyer_html = f"""
            <h2>Payment processing failed</h2>
            <p>Dear {buyer.username},</p>
            <p>Unfortunately, your payment of ₹{transaction.amount:,.2f} for the {car.year} {car.company} {car.name} could not be processed.</p>
            <p>Transaction ID: {transaction.transaction_id}</p>
            <p>Please try again or use a different payment method.</p>
            <p>If you continue to experience issues, please contact our support team.</p>
            <p>Thank you for using Car Deal Hub!</p>
            """
            
            buyer_message = Mail(
                from_email=Email(from_email),
                to_emails=To(buyer.email),
                subject=buyer_subject,
                html_content=Content("text/html", buyer_html)
            )
            
            # Send email
            sg = SendGridAPIClient(sendgrid_key)
            sg.send(buyer_message)
            
            logging.info(f"Transaction failed email sent for transaction {transaction_id}")
            return True
            
        else:
            logging.error(f"Unknown notification type: {notification_type}")
            return False
            
    except Exception as e:
        logging.error(f"Failed to send transaction email: {str(e)}")
        return False