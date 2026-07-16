import stripe
from flask import current_app
from app.models.payment import Payment
from app.models.order import Order
from app.utils.errors import PaymentError
from app import db


class PaymentService:
    """Service for handling payment processing with Stripe."""
    
    @staticmethod
    def initialize_stripe():
        """Initialize Stripe with API key."""
        stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
    
    @staticmethod
    def create_payment_intent(amount, currency='usd', metadata=None):
        """
        Create a Stripe payment intent.
        
        Args:
            amount: Amount in dollars (will be converted to cents)
            currency: Currency code (default: usd)
            metadata: Optional metadata dictionary
        
        Returns:
            dict: Payment intent details
        """
        PaymentService.initialize_stripe()
        
        try:
            # Convert dollars to cents
            amount_cents = int(float(amount) * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True}
            )
            
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': amount,
                'currency': currency
            }
        except stripe.error.StripeError as e:
            raise PaymentError(f"Payment intent creation failed: {str(e)}")
    
    @staticmethod
    def confirm_payment(payment_intent_id):
        """
        Confirm a payment intent.
        
        Args:
            payment_intent_id: Stripe payment intent ID
        
        Returns:
            dict: Payment confirmation details
        """
        PaymentService.initialize_stripe()
        
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                return {
                    'status': 'succeeded',
                    'amount': intent.amount / 100,
                    'currency': intent.currency,
                    'payment_method': intent.payment_method
                }
            else:
                return {
                    'status': intent.status,
                    'error': intent.last_payment_error.message if intent.last_payment_error else None
                }
        except stripe.error.StripeError as e:
            raise PaymentError(f"Payment confirmation failed: {str(e)}")
    
    @staticmethod
    def create_payment_record(order, payment_intent_data):
        """
        Create payment record in database.
        
        Args:
            order: Order object
            payment_intent_data: Payment intent data from Stripe
        
        Returns:
            Payment: Created payment record
        """
        payment = Payment(
            order_id=order.id,
            payment_method='card',
            payment_status='processing',
            amount=order.total,
            currency='USD',
            stripe_payment_intent_id=payment_intent_data.get('payment_intent_id')
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return payment
    
    @staticmethod
    def update_payment_from_webhook(payment_intent):
        """
        Update payment record from Stripe webhook.
        
        Args:
            payment_intent: Stripe payment intent object
        
        Returns:
            Payment: Updated payment record
        """
        payment = Payment.query.filter_by(
            stripe_payment_intent_id=payment_intent.id
        ).first()
        
        if not payment:
            return None
        
        if payment_intent.status == 'succeeded':
            payment.mark_as_succeeded()
            payment.stripe_charge_id = payment_intent.charges.data[0].id if payment_intent.charges.data else None
            
            # Update payment method details
            if payment_intent.charges.data:
                charge = payment_intent.charges.data[0]
                payment_method = charge.payment_method_details.card
                payment.card_last4 = payment_method.last4
                payment.card_brand = payment_method.brand
                payment.card_exp_month = payment_method.exp_month
                payment.card_exp_year = payment_method.exp_year
            
            # Update order status
            order = payment.order
            order.update_status('processing')
            
        elif payment_intent.status == 'payment_failed':
            error = payment_intent.last_payment_error
            payment.mark_as_failed(
                failure_code=error.code if error else None,
                failure_message=error.message if error else 'Payment failed'
            )
            
            # Update order status
            order = payment.order
            order.update_status('cancelled')
        
        db.session.commit()
        return payment
    
    @staticmethod
    def process_refund(payment, amount=None, reason=None):
        """
        Process a refund for a payment.
        
        Args:
            payment: Payment object
            amount: Refund amount (None for full refund)
            reason: Refund reason
        
        Returns:
            dict: Refund details
        """
        PaymentService.initialize_stripe()
        
        if not payment.stripe_charge_id:
            raise PaymentError("No charge ID found for this payment")
        
        try:
            refund_amount = amount or payment.amount
            refund_cents = int(float(refund_amount) * 100)
            
            refund = stripe.Refund.create(
                charge=payment.stripe_charge_id,
                amount=refund_cents,
                reason=reason or 'requested_by_customer'
            )
            
            # Update payment record
            payment.process_refund(refund_amount, reason)
            
            # Update order status
            order = payment.order
            order.update_status('refunded')
            
            db.session.commit()
            
            return {
                'refund_id': refund.id,
                'amount': refund_amount,
                'status': refund.status
            }
        except stripe.error.StripeError as e:
            raise PaymentError(f"Refund failed: {str(e)}")
