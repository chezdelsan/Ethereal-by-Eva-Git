"""
Email service using Resend.
Sends order confirmations and admin notifications.
"""

import resend
from config import settings

# Configure Resend
resend.api_key = settings.resend_api_key


def format_price(cents: int) -> str:
    """Format cents to dollar string."""
    return f"${cents / 100:.2f}"


def send_customer_confirmation(order: dict, items: list) -> bool:
    """Send order confirmation email to customer."""
    if not settings.resend_api_key:
        print("⚠️  No Resend API key - skipping customer email")
        return False
    
    items_html = "".join([
        f'<tr><td style="padding: 10px; border-bottom: 1px solid #eee;">{item["title"]}</td>'
        f'<td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">{format_price(item["price"])}</td></tr>'
        for item in items
    ])
    
    address = order["shipping_address"]
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #000; border-bottom: 2px solid #000; padding-bottom: 10px;">
            Thank You for Your Order!
        </h1>
        
        <p>Hi {order["customer_name"]},</p>
        
        <p>Your order has been confirmed. Each piece is one-of-a-kind and will be carefully packaged for shipping.</p>
        
        <h2 style="color: #000; font-size: 18px; margin-top: 30px;">Order #{order["id"]}</h2>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <thead>
                <tr style="background: #f5f5f5;">
                    <th style="padding: 10px; text-align: left;">Item</th>
                    <th style="padding: 10px; text-align: right;">Price</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
                <tr>
                    <td style="padding: 10px;">Shipping (USPS Priority)</td>
                    <td style="padding: 10px; text-align: right;">{format_price(order["shipping_cost"])}</td>
                </tr>
                <tr style="font-weight: bold; font-size: 18px;">
                    <td style="padding: 15px 10px; border-top: 2px solid #000;">Total</td>
                    <td style="padding: 15px 10px; border-top: 2px solid #000; text-align: right;">{format_price(order["total"])}</td>
                </tr>
            </tbody>
        </table>
        
        <h2 style="color: #000; font-size: 18px; margin-top: 30px;">Shipping To</h2>
        <p style="background: #f5f5f5; padding: 15px;">
            {address["name"]}<br>
            {address["street"]}<br>
            {address["city"]}, {address["state"]} {address["zip"]}
        </p>
        
        <p style="margin-top: 30px; color: #666; font-size: 14px;">
            We'll send you tracking information once your order ships.
        </p>
        
        <p style="margin-top: 30px;">
            With love,<br>
            <strong>Ethereal by Eva</strong>
        </p>
    </div>
    """
    
    try:
        resend.Emails.send({
            "from": settings.from_email,
            "to": order["customer_email"],
            "subject": f"Order Confirmed - Ethereal by Eva #{order['id']}",
            "html": html,
        })
        print(f"✅ Customer confirmation sent to {order['customer_email']}")
        return True
    except Exception as e:
        print(f"❌ Failed to send customer email: {e}")
        return False


def send_admin_notification(order: dict, items: list) -> bool:
    """Send new order notification to admin."""
    if not settings.resend_api_key or not settings.admin_email:
        print("⚠️  No Resend API key or admin email - skipping admin notification")
        return False
    
    items_text = "\n".join([f"  - {item['title']}: {format_price(item['price'])}" for item in items])
    address = order["shipping_address"]
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #008800; border-bottom: 2px solid #008800; padding-bottom: 10px;">
            🎉 New Sale!
        </h1>
        
        <h2 style="font-size: 32px; margin: 20px 0;">{format_price(order["total"])}</h2>
        
        <h3>Order #{order["id"]}</h3>
        
        <p><strong>Customer:</strong> {order["customer_name"]}<br>
        <strong>Email:</strong> {order["customer_email"]}</p>
        
        <h3>Items Sold</h3>
        <ul>
            {"".join([f"<li>{item['title']} - {format_price(item['price'])}</li>" for item in items])}
        </ul>
        
        <h3>Ship To</h3>
        <p style="background: #f5f5f5; padding: 15px;">
            {address["name"]}<br>
            {address["street"]}<br>
            {address["city"]}, {address["state"]} {address["zip"]}
        </p>
        
        <p style="margin-top: 30px; padding: 15px; background: #ffffcc; border-left: 4px solid #ffcc00;">
            <strong>Action needed:</strong> Package and ship this order, then update the tracking number.
        </p>
    </div>
    """
    
    try:
        resend.Emails.send({
            "from": settings.from_email,
            "to": settings.admin_email,
            "subject": f"💰 New Sale: {format_price(order['total'])} - Order #{order['id']}",
            "html": html,
        })
        print(f"✅ Admin notification sent to {settings.admin_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send admin email: {e}")
        return False
