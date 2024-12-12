# this file contains all user authentication routes
import os

import jwt
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, make_response
from app import database
from app.models.user_models import PendingUser, RegisteredUser
from app.utils.user_authentication_utils import generate_verification_token, send_verification_email, decode_verification_token

authentication_blueprint= Blueprint('auth', __name__)

# homepage routing
@authentication_blueprint.route('/', methods=['GET'])
def homepage():
    return f'<h1>Welcome to the homepage</h1>'


# user authentication routes
# registration routing
@authentication_blueprint.route('/register', methods=['POST'])
def register():
    try:
        # collect POST data information from signup forms client-side
        data= request.get_json()
        name= data.get('name')
        surname= data.get('surname')
        email= data.get('email')
        password= data.get('password')

        # query user email to check if it exists in database first
        pending_user_exists= PendingUser.query.filter_by(email=email).first()
        registered_user_exists= RegisteredUser.query.filter_by(email=email).first()
        user_in_system= pending_user_exists, registered_user_exists

        if user_in_system:
            if pending_user_exists:
                return jsonify({'message':'User email already pending verification!'}), 400
            if registered_user_exists:
                return jsonify({'message':'User email already exists!'}), 400

        
        # if user does not already exist in database, assign POST data details to pending user until user verifies email
        # to verify email, generate temporary token and send to pending user email
        pending_user = PendingUser(
            name=name,
            surname=surname,
            email=email,
            password=password
        )
        database.session.add(pending_user)  # add pending user to database, to be deleted after user verifies email
        database.session.commit()

        # generate temporary verification token to be sent to pending user
        token = generate_verification_token(email)

        status_code, message= send_verification_email(email, token)

        if status_code== 500:
            return jsonify({'error': message})

        # if status_code = 200, store pending user in temp http-only encrypted cookie
        response = make_response(jsonify({'message': message}), 200)

        response.set_cookie(
            'pending_user',
            value=token,
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=1800
        )

        return response  # verification email sent successfully, pending user details temporarily stored in http-only cookie

    except Exception as e:
        database.session.rollback()
        return jsonify({'error':f'An error occurred while registering user, {e}.'}), 400


# email verification routing
@authentication_blueprint.route('/verify-email', methods=['GET'])
def verify_token():

    # user checks their email for verification email and clicks on the link
    # verification link redirects to this route
    # decoding token is expected to return user email instead of payload to prevent possible token abuse
    try:
        token= request.args.get('token')
        if not token:
            return jsonify({'error':'Verification token is missing!'}), 400

        payload= decode_verification_token(token)
        if isinstance(payload, str):
            expected_email= payload
        else:
            expected_email= payload.get('email')

        if not expected_email:
            return jsonify({'error':'Invalid token, email not found!'}), 400

        # retrieve pending user data from cookie
        pending_user_cookie= request.cookies.get('pending_user')
        if not pending_user_cookie:
            return jsonify({'error':'Missing pending user cookie!'}), 400

        # check if email is already verified and registered in database
        user_exists= RegisteredUser.query.filter_by(email=expected_email).first()
        if user_exists:
            return jsonify({'message': 'Email is already registered!'}), 400

        secret_key = os.getenv('JWT_SECRET_KEY')
        pending_user_details = jwt.decode(pending_user_cookie, secret_key, algorithms=['HS256'])
        pending_user_email = pending_user_details.get('email')

        pending_user_exists = PendingUser.query.filter_by(email=pending_user_email).first()
        if not pending_user_exists:
            return jsonify({'message': 'Pending user details not found!'}), 400

        # verify if email from token matches that from pending user
        if expected_email != pending_user_email:
            return jsonify({'message': 'Email from token does not match pending user email!'}), 400

        # if user does not exist, redirect to a new page and ask if they want to be a client or servicer
        # logic for either routes goes here
        # for now, we will assume user wants to be just a client

        new_user = RegisteredUser(
            name=pending_user_exists.name,
            surname=pending_user_exists.surname,
            email=pending_user_exists.email,
        )
        new_user.set_password(pending_user_exists.password)

        database.session.add(new_user)
        database.session.delete(pending_user_exists)
        database.session.commit()

        # clear the token cookie
        response= make_response(jsonify({'message':'Email verified. New client user registered successfully!!'}))
        response.delete_cookie('pending_user')

        # send user registration confirmation message

        return response, 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error':'Verification token has expired!'}), 400
    except jwt.InvalidTokenError:
        return jsonify({'error':'Invalid token!'}), 400


# user login route
@authentication_blueprint.route('/login', methods=['POST'])
def login():
    try:
        # collect client-validated user login details, empty fields to be handled client-side
        data= request.get_json()
        email= data.get('email')
        password= data.get('password')

        # fetch specific attributes to reduce query time
        user = RegisteredUser.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify({'message':'Invalid login credentials!'}), 401

        # generate token for user login session if user exists
        payload= {
            'sub':user.id,
            'user_id': user.id,
            'exp': datetime.now(timezone.utc)+ timedelta(hours=3)
        }
        token= jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')

        # create response and set the cookie
        response= make_response(jsonify({
            'message':'User logged in successfully!',
            'token': token,
        }))
        response.set_cookie(
            'token',
            token,
            httponly= True,
            secure= True,
            samesite= 'Strict'
        )

        return response, 200

    except Exception as e:
        return jsonify({'error':f'An internal error occurred! {e}'}), 500