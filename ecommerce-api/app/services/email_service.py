from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from flask import current_app, render_template_string
from app.utils.errors import APIError


class EmailService:
    """Service for sending emails via SendGrid."""
    
    @staticmethod
    def send_email(to_email, subject, html_content, from_email=None):
        """
        Send an email using SendGrid.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of email
            from_email: Sender email (optional, uses config default)
        
        Returns:
            bool: True if sent successfully
        """
        api_key = current_app.config.get('SENDGRID_API_KEY')
        
        # In testing mode, just log and return
        if current_app.config.get('TESTING'):
            current_app.logger.info(f"[TEST MODE] Email to {to_email}: {subject}")
            return True
        
        if not api_key or api_key == 'mock_sendgrid_key':
            current_app.logger.warning("SendGrid API key not configured, skipping email")
            return False
        
        try:
            from_email = from_email or current_app.config.get('FROM_EMAIL')
            
            message = Mail(
                from_email=Email(from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            sg = SendGridAPIClient(api_key)
            response = sg.send(message)
            
            return response.status_code in [200, 201, 202]
        except Exception as e:
            current_app.logger.error(f"Email sending failed: {str(e)}")
            return False
    
    @staticmethod
    def send_order_confirmation(order):
        """
        Send order confirmation email.
        
        Args:
            order: Order object
        
        Returns:
            bool: True if sent successfully
        """
        subject = f"Order Confirmation - {order.order_number}"
        
        # Build items list
        items_html = ""
        for item in order.items:
            items_html += f"""
            <tr>
                <td>{item.product_name}</td>
                <td>{item.quantity}</td>
                <td>${item.price:.2f}</td>
                <td>${item.total_price:.2f}</td>
            </tr>
            """
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #4CAF50; color: white; }}
                .total {{ font-size: 18px; font-weight: bold; text-align: right; }}
                .footer {{ text-align: center; padding: 20px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Thank You for Your Order!</h1>
                </div>
                <div class="content">
                    <p>Hi {order.shipping_first_name},</p>
                    <p>Your order has been confirmed and will be shipped soon.</p>
                    
                    <h2>Order Details</h2>
                    <p><strong>Order Number:</strong> {order.order_number}</p>
                    <p><strong>Order Date:</strong> {order.created_at.strftime('%B %d, %Y')}</p>
                    
                    <h3>Items Ordered</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Price</th>
                                <th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <table>
                        <tr>
                            <td colspan="3" style="text-align: right;"><strong>Subtotal:</strong></td>
                            <td>${order.subtotal:.2f}</td>
                        </tr>
                        {f'<tr><td colspan="3" style="text-align: right;"><strong>Discount:</strong></td><td>-${order.discount_amount:.2f}</td></tr>' if order.discount_amount > 0 else ''}
                        <tr>
                            <td colspan="3" style="text-align: right;"><strong>Shipping:</strong></td>
                            <td>${order.shipping_cost:.2f}</td>
                        </tr>
                        <tr>
                            <td colspan="3" style="text-align: right;"><strong>Tax:</strong></td>
                            <td>${order.tax_amount:.2f}</td>
                        </tr>
                        <tr class="total">
                            <td colspan="3" style="text-align: right;"><strong>Total:</strong></td>
                            <td>${order.total:.2f}</td>
                        </tr>
                    </table>
                    
                    <h3>Shipping Address</h3>
                    <p>
                        {order.shipping_first_name} {order.shipping_last_name}<br>
                        {order.shipping_street_address}
                        {f', {order.shipping_apartment}' if order.shipping_apartment else ''}<br>
                        {order.shipping_city}, {order.shipping_state} {order.shipping_postal_code}<br>
                        {order.shipping_country}
                    </p>
                    
                    <p>We'll send you a shipping confirmation email as soon as your order ships.</p>
                </div>
                <div class="footer">
                    <p>Thank you for shopping with us!</p>
                    <p>If you have any questions, please contact our support team.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(
            to_email=order.shipping_email,
            subject=subject,
            html_content=html_content
        )
    
    @staticmethod
    def send_shipping_confirmation(order, tracking_number=None):
        """
        Send shipping confirmation email.
        
        Args:
            order: Order object
            tracking_number: Optional tracking number
        
        Returns:
            bool: True if sent successfully
        """
        subject = f"Your Order Has Shipped - {order.order_number}"
        
        tracking_html = ""
        if tracking_number:
            tracking_html = f"<p><strong>Tracking Number:</strong> {tracking_number}</p>"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Your Order Has Shipped!</h1>
                </div>
                <div class="content">
                    <p>Hi {order.shipping_first_name},</p>
                    <p>Great news! Your order {order.order_number} has been shipped and is on its way to you.</p>
                    
                    {tracking_html}
                    
                    <p><strong>Shipping Address:</strong><br>
                    {order.shipping_street_address}<br>
                    {order.shipping_city}, {order.shipping_state} {order.shipping_postal_code}</p>
                    
                    <p>Thank you for your order!</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(
            to_email=order.shipping_email,
            subject=subject,
            html_content=html_content
        )
