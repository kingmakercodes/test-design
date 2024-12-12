import os
import jwt
from datetime import datetime, timedelta, timezone
from flask_mail import Message
from app import mail
from tenacity import retry, stop_after_attempt, wait_exponential
from app.utils.validator import validate_base_url

jwt_secret_key = os.getenv('JWT_SECRET_KEY')
base_url= validate_base_url(os.getenv('BASE_URL')) # modified to be validated before usage
sender= os.getenv('MAIL_USERNAME')


# generate verification token function
def generate_verification_token(email):
    # this function will generate a random token for provided email argument
    try:

        payload= {
            'email':email,
            'exp': datetime.now(timezone.utc)+ timedelta(minutes=30)
        }
        return jwt.encode(payload, jwt_secret_key, algorithm='HS256')

    except Exception as e:
        return f'error: An error occurred while generating verification token, {e}.'


# decode verification token function
def decode_verification_token(token):

    # this function will decode valid encoded verification token sent to email
    try:
        return jwt.decode(token, jwt_secret_key, algorithms=['HS256'])

    except jwt.ExpiredSignatureError:
        raise ValueError('error: Expired token!')
    except jwt.InvalidTokenError:
        raise ValueError('error: Invalid token!')


# send verification email to verified email function. this function will retry if fail
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def send_verification_email(email, token):
    try:
        verification_route= f'{base_url}/verify-email?token={token}'

        # create email message to be sent. configurations for email to be defined in config.py
        subject= 'Email Verification:'
        body= (f'Please click on this link to verify your email:\n\n '
               f'{verification_route}\n\n'
               f'If you have any issues verifying your email, please contact customer support.\n'
               f'This is no-reply verification email, please do not reply this email.'
               )
        msg= Message(
            subject=subject,
            recipients=[email],
            body=body,
            sender=sender
        )

        # send email
        mail.send(msg)

        return 200, f'Verification mail successfully sent, please check your email.'

    except Exception as e:
        return 500, f'Failed to send verification email to {email}: {e}'


# send confirmation email to user email after successful registration
def send_confirmation_email(email, name):

    subject= 'Registration successful'
    body= (
        f'Dear {name}, \n\n'
        f'Your email has successfully been verified. You can now use your AlloMaison account. \n'
        f'If you have any questions or issues regarding anything, please contact our customer support team. \n'
        f'Thank you for joining us! \n\n'
        f'Best regards, \n'
        f'The AlloMaison Team.\n\n'
        f'This is no-reply verification email, please do not reply this email.'
    )
    msg= Message(
        subject=subject,
        recipients=[email],
        body=body,
        sender=sender
    )
    mail.send(msg)