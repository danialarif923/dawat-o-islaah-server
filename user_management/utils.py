import threading
from dawat_o_islaah.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS
from django.core.mail import EmailMessage, get_connection
from django.utils.html import strip_tags

def send_mail(subject, html_message, email_from, recipient_list):
    """
    Sends an HTML email using Django's EmailMessage.
    """
    with get_connection(
            host=EMAIL_HOST,
            port=EMAIL_PORT,
            username=EMAIL_HOST_USER,
            password=EMAIL_HOST_PASSWORD,
            use_tls=EMAIL_USE_TLS
    ) as connection:
        plain_message = strip_tags(html_message)
        email = EmailMessage(
            subject,
            plain_message,
            email_from,
            recipient_list,
            connection=connection
        )
        email.content_subtype = "html"
        email.body = html_message
        email.send()

def send_forget_password_email(first_name, email, absurl):
    subject = '🔒 Reset Your Password - Dawat-e-Islah'
    email_from = EMAIL_HOST_USER
    recipient_list = [email]

    html_message = f'''
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .header {{
                background-color: #2c5f2d;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .content {{
                padding: 20px;
            }}
            .footer {{
                background-color: #f4f4f4;
                padding: 10px;
                text-align: center;
                font-size: 0.9em;
            }}
            .btn {{
                display: inline-block;
                padding: 10px 20px;
                margin: 20px 0;
                background-color: #2c5f2d;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Password Reset Request</h1>
        </div>
        
        <div class="content">
            <p>Dear {first_name},</p>
            <p>We received a request to reset your password. If you made this request, please click the button below to proceed:</p>
            
            <a style="color:white" href="{absurl}" class="btn">Reset Your Password</a>
            
            <p>If you did not request a password reset, please ignore this email or contact support.</p>
            
            <p>Jazakum Allah Khairan,</p>
            <p>The Dawat-e-Islah Team</p>
        </div>
        
        <div class="footer">
            <p>Need help? Contact us at <a href="mailto:support@dawateislah.com">support@dawateislah.com</a></p>
        </div>
    </body>
    </html>
    '''

    email_thread = threading.Thread(target=send_mail, args=(subject, html_message, email_from, recipient_list))
    email_thread.start()
