""" Main app.py page For managing Routes """

import os
import re
from collections import defaultdict

# Non Standard Imports
import json
import pyotp
import qrcode
import sqlite3
import requests

# Flask Imports
from flask import (
    Flask,
    redirect,
    url_for,
    render_template,
    request,
    flash,
    jsonify
)

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user
)

from oauthlib.oauth2 import WebApplicationClient

# Global Configuration
from config import Config

# Application Imports
from databasemanager.database import (
    load_csv_data,
    db,
    migrate,
    bcrypt
)

from databasemanager.processing import (
    DatabaseRisk,
    DatabaseHistoricalData,
    DatabaseCryptoList,
    DatabaseUserList,
    DatabaseUpdateCrypto,
    DatabaseCryptoUpdatedResults
)

from utils.otp import CryptoOTP
from utils.generic import GenericUtils

from Models import (
    User,
    CryptoList,
    LocalUser,
    LocalUser_Login
)

from endpointmanager.data_downloader import download
from endpointmanager.endpoint import Endpoint

from random import randint

# Define the App Module
app = Flask(__name__, static_url_path='/static')
app.secret_key = app.config.get('SECRET_KEY')
app.config.from_object(Config)

# Authentication Management
auth_manager = LoginManager()
auth_manager.login_message_category = "info"
auth_manager.session_protection = "strong"
auth_manager.init_app(app)

# Constants for OAUTH / GCP as a provider
GOOGLE_CLIENT_SECRET = app.config.get('GOOGLE_CLIENT_SECRET')
GOOGLE_CLIENT_ID = app.config.get('GOOGLE_CLIENT_ID')
DISCOVERY_URL = app.config.get('DISCOVERY_URL')
DEBUGGING = app.config.get('DEBUGGING')

def create_app():
    return app

# Initialize the DB on Startup
try:
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Create Tables within context
    with app.app_context():
        db.create_all()
except Exception as exc:
    raise RuntimeError("Unable to initialize Database") from exc

# OAUTH Web client
web_client = WebApplicationClient(GOOGLE_CLIENT_ID)

def pull_config():
    """ Retrieve OAUTH Config """

    return requests.get(DISCOVERY_URL, timeout=20).json()

@auth_manager.user_loader
def find_user(user_id):
    """ Fetch User """

    return User.get(user_id)


@app.route('/')
def home():
    """ Web Application Landing Page """
    is_profile_complete = False
    results = []

    if current_user.is_authenticated:
        if User.is_profile_data_complete(current_user):
            is_profile_complete = True
            calcrisk = DatabaseRisk()
            results = calcrisk.execute_processing_query(current_user.id)
        
        return render_template("home.html", is_profile_complete=is_profile_complete, recommended_investments=results)
    else:
        return render_template("index_guest.html")

@app.route('/faq')
def faq():
    return render_template("faq.html")

@app.route('/login')
def initiate_login():
    """ Initiate Web Application Login """

    _config = pull_config()
    auth_endpoint = _config["authorization_endpoint"]

    request_uri = web_client.prepare_request_uri(
        auth_endpoint,
        redirect_uri=request.base_url + "/redirect",
        scope=["openid", "email", "profile"]
    )

    return redirect(request_uri)


@app.route("/login/redirect", methods=['POST', 'GET'])
def authenticate_callback():
    """ OAUTH Callback to communicate with Provider """

    c = request.args.get("code")
    _config = pull_config()
    _endpoint = _config["token_endpoint"]

    # Form request to get Token
    token_url, headers, body = web_client.prepare_token_request (
        _endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=c,
    )

    # Send data to Provider Get => Token
    tresponse = requests.post (
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        timeout=10
    )

    # Parse Response
    web_client.parse_request_body_response(json.dumps(tresponse.json()))

    # Collect User Data
    user_info = _config["userinfo_endpoint"]
    uri, headers, body = web_client.add_token(user_info)
    userresponse = requests.get(
        uri,
        headers=headers,
        data=body,
        timeout=10
    )

    # Gather User Information
    if userresponse.json().get("email_verified"):
        user_id = userresponse.json()["sub"]
        email = userresponse.json()["email"]
        n = userresponse.json()["given_name"]
    else:
        return "Unverified", 400

    # validation built into method
    user = User(id=user_id, name=n, email=email)
    user.update_users(user)

    # Initiate Login and return
    login_user(user)

    return redirect(url_for("home"))

@app.route('/guest_login')
def guest_login():
    return render_template("guest_login.html")

@app.route('/guest_login',methods=["POST"])
def guest_login_post():
    username = request.form.get('username').upper()
    password = request.form.get('password')
    
    # create a user in the local users table
    user = LocalUser_Login()
    hashedPw = user.GetHashedPw()
    
    if hashedPw != None and bcrypt.check_password_hash(hashedPw, password):
        user = user.Get_User()

        # validation built into method
        user = User(id=user.id, name=user.name, email=user.email)
        user.update_users(user)

        # Initiate Login and return
        login_user(user)

        return redirect(url_for("home"))
    else:
        flash("Invalid credentials", "error")

        return redirect(url_for("guest_login"))
    

@app.route('/guest_register')
def guest_register():
    return render_template("guest_register.html")

@app.route('/guest_register', methods=["POST"])
def guest_register_post():
    username = request.form.get('username').upper()
    email = request.form.get('email')
    password = request.form.get('password')
    confirmPassword = request.form.get('confirmPassword')
    user_id = str(randint(100000000000000000000, 1000000000000000000000))

    # If the passwords do not match
    if password != confirmPassword:
        ## TODO Add user feedback
        flash("Passwords must match", "warning")

        return redirect(url_for("guest_register"))

    ## hash the password
    password = bcrypt.generate_password_hash(password).decode('utf-8')

    # create a user in the local users table
    localUser = LocalUser(id="", 
                          user_id=user_id, 
                          password=password, 
                          name=username,
                          email=email)
    if not localUser.verify():
        return redirect(url_for("guest_register"))
    else:
        localUser.register(localUser)
        # create a user in the user table
        user = User(id=user_id, name=username, email=email)
        user.update_users(user)
        
        flash("User created", "success")
        return redirect(url_for("guest_login"))
    

# @app.route('/local_login', methods=['GET', 'POST'])
# def dev_login():
#     """ Route For allowing Non Oauth Login """

#     otp = CryptoOTP()
#     qrauth = otp.generate_provision_url("test@gmail.com")
#     qrcode.make(qrauth).save("qr_auth_test.png")
#     hotp_qr = pyotp.HOTP(otp.basesecret)


#     user = User(id_=user_id, name=name, email=email)

#     # If this dev user doesn't exist, create one
#     if not User.get(user_id):
#         User.create(user_id, name, email, profile_pic)

#     # Log the dev user in
#     login_user(user)

#     return redirect(url_for("home"))


@app.route("/logout")
@login_required
def initiate_logout():
    """ Log User Out """

    logout_user()

    return redirect(url_for("home"))


def is_valid_amount(amount):
    """ Regex to validate Amount """

    return bool(re.match(r'^\d+(\.\d{0,2})?$', amount))


@app.route('/user_profile', methods=['GET', 'POST'])
# @login_required
def user_profile():
    """ Return User Profile Information """

    if current_user.is_authenticated:

        if request.method == 'POST':
            # email = request.form['inputEmail'] # Don't use as they should come from Google auth
            # name = request.form['inputName']   # Don't use as they should come from Google auth
            name = None
            gross_income_range  = request.form['inputIncomeRange']
            investment_amount   = request.form['inputInvestmentAmount']
            investment_risk     = request.form['inputInvestmentRisk']
            investment_amount   = request.form['inputInvestmentAmount']

            if not is_valid_amount(investment_amount):
                flash('There was an error updating your profile.', 'danger')
                flash('Please enter a valid investment amount without any currency symbols.', 'danger')
                return redirect(url_for('user_profile'))

            User.save_profile_data(
                current_user,
                gross_income_range,
                investment_amount,
                investment_risk
            )

        profile_data = User.get_profile_data(current_user)

        return render_template("user_profile.html", user=profile_data)
    else:

        return render_template("index_guest.html")


@app.route('/user_list', methods=['GET', 'POST'])
def user_list():
    """ Return List of Users """

    #fetch_users = DatabaseUserList()
    #results = fetch_users.execute_processing_query(cuser=current_user)

    return render_template('user_list.html')

@app.route('/user_list_json', methods=['GET', 'POST'])
def user_list_json():
    """ User List JSON Format"""

    fetch_users = DatabaseUserList()
    results = fetch_users.execute_processing_query()

    formatted_data = [
        {
            "id": user.id,
            "name":user.name,
            "email": user.email,
            "gross_income_range": user.gross_income_range,
            "investment_amount": user.investment_amount,
            "investment_risk": user.investment_risk,
            "is_admin": user.is_admin
        }
        for user in results
    ]

    return jsonify(data=formatted_data)

@app.route('/user_list_update_data', methods=['POST'])
def update_user_data():


    # Format to Multidict
    rform = GenericUtils.datatables_extract_data_form(request.form)

    try:
        recordid, inner_dict = next(iter(rform.items()))
        column = next(iter(inner_dict.keys()))

        newrecord = rform[recordid][column]
    except KeyError as e:
        print("error", e)

    if recordid is None:
        return None
    
    
    user = User.update_user_by_field(recordid, column, newrecord)

    formatted_data = []
    if user is not None:
        formatted_data = [
            {
                "id": user.id,
                "name":user.name,
                "email": user.email,
                "gross_income_range": user.gross_income_range,
                "investment_amount": user.investment_amount,
                "investment_risk": user.investment_risk,
                "is_admin": user.is_admin

            }
            #for currency in results
        ]

    return jsonify(data=formatted_data)


@app.route('/crypto_list', methods=['GET', 'POST'])
def crypto_list():
    """ Return List of Crypto Currencies """

    if request.method == 'POST':
        if request.form["updateOperation"] == "updateCryptoList":
            CryptoList.load_csv_data()

    fetch_crypto = DatabaseCryptoList()
    results = fetch_crypto.execute_processing_query(cuser=current_user)

    return render_template('crypto_list.html', currencies=results)


@app.route('/crypto_list_json', methods=['GET', 'POST'])
def crypto_list_json():
    """ Crypto Stock List JSON Format"""

    fetch_crypto = DatabaseCryptoList()
    results = fetch_crypto.execute_processing_query()
    
    formatted_data = [
        {
            "id": currency.id,
            "code": currency.code,
            "is_active":currency.is_active,
            "desc": currency.desc,
            "code_AG": currency.code_AG,
            "code_CG": currency.code_CG,
            "code_FMP": currency.code_FMP
        }
        for currency in results
    ]

    return jsonify(data=formatted_data)
    #return results


@app.route('/crypto_history', methods=["GET", 'POST'])
def crypto_history():
    """ this endpoint downloads the data from all api and dumps into the database tables """

    if request.method == 'POST':
        if request.form["updateOperation"] == "downloadFMPHistoryFull":
            historical_fp = Endpoint("historical_FP")
            download(historical_fp, app)

    historical_data = DatabaseHistoricalData()
    results = historical_data.execute_processing_query()
    print(f"crypto_history records: {len(results)}")
    formatted_data = [
        {
            "coin": currency.coin,
            "avg_change_percent": currency.avg_change_percent,
            "avg_change_over_time":currency.avg_change_over_time,
            "avg_price_low": currency.avg_price_low,
            "avg_price_high": currency.avg_price_high,
            "min_price_low": currency.min_price_low,
            "max_price_high": currency.max_price_high
        }
        for currency in results
    ]

    return render_template("crypto_history.html", FPM_crypto_history=formatted_data)


@app.route('/crypto_list_update_data', methods=['POST'])
def update_crypto_data():
    """ Refresh Crypto data  """

    # Format to Multidict
    rform = GenericUtils.datatables_extract_data_form(request.form)

    try:
        recordid, inner_dict = next(iter(rform.items()))
        column = next(iter(inner_dict.keys()))

        newrecord = rform[recordid][column]
    except KeyError as e:
        print("error", e)

    if recordid is None:
        return None

    update_crypto = DatabaseUpdateCrypto()
    results = update_crypto.execute_processing_query(
        column,
        newrecord,
        recordid,
    )

    fetch_updated = DatabaseCryptoUpdatedResults()
    print(f"recordid={recordid}")
    results = fetch_updated.execute_processing_query(recordid)

    # Format the data
    formatted_data = [
        {
            "id": currency.id,
            "code": currency.code,
            "is_active":currency.is_active,
            "desc": currency.desc,
            "code_AG": currency.code_AG,
            "code_CG": currency.code_CG,
            "code_FMP": currency.code_FMP
        }
        for currency in results
    ]

    return jsonify(data=formatted_data)


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True, ssl_context="adhoc")
