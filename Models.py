""" Manage User Accounts in Database """

# Import STD
import os

# Import CSV and third party
import csv

# Flask Imports
from flask import (
    flash,
    current_app
)

from flask_wtf import FlaskForm
from flask_login import UserMixin

from wtforms import (
    StringField,
    PasswordField
)

from wtforms.validators import (
    InputRequired,
    Length,
    Regexp,
    Email,
    EqualTo,
    ValidationError
)

# app imports
from databasemanager.database import db

from databasemanager.processing import (
    DatabaseRiskUpdate,
    CryptoListLoadDataTransaction,
    CryptoListLoadDataExec,
    DatabaseGetCryptoCodeByAPI,
    DatabaseUpdateUser
)

# SQLAlchemy Import
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import text
import json

from random import randint

class User(UserMixin, db.Model):
    """ User object """

    __tablename = 'user'
    id      = db.Column(db.Text, primary_key=True)
    name    = db.Column(db.String(80), unique=True, nullable=False)
    email   = db.Column(db.String(120), unique=True, nullable=False)

    # Non default User info
    gross_income_range  = db.Column(db.Text, unique=False, nullable=True)
    investment_amount   = db.Column(db.Integer, unique=False, nullable=True)
    investment_risk     = db.Column(db.Text, unique=False, nullable=True)
    is_admin            = db.Column(db.Boolean, unique=False, nullable=True)

    def __repr__(self):
        return f"<User {self.name}>"

    def update_users(self, user):
        """ update database with user entry """

        if not isinstance(user, __class__):
            raise ValueError("User Should be an object of this Class")

        existing_user = db.session.query(User).filter_by(id=user.id).first()

        if existing_user:
            existing_user.id    = user.id
            existing_user.name  = user.name
            existing_user.email = user.email
            # we don't want to lose the followin data when authenticating again.
            # existing_user.gross_income_range    = user.gross_income_range
            # existing_user.investment_amount     = user.investment_amount
            # existing_user.investment_risk       = user.investment_risk
            #existing_user.is_admin              = user.is_admin
        else:
            db.session.add(user)
        
        db.session.commit()

    @staticmethod
    def update_user_by_field(user_id, column_name, column_value):
        """ update database from datatables grid/list """
        print(f"user_id={user_id}")
        existing_user = db.session.query(User).filter_by(id=str(user_id)).first()
        print(f"user infield update: {column_name} = {column_value}")
        
        if existing_user:
            update_crypto = DatabaseUpdateUser()
            results = update_crypto.execute_processing_query(
            column_name,
            column_value,
            user_id,
            )
            
        #return record
        return db.session.query(User).filter_by(id=str(user_id)).first()

    @staticmethod
    def is_profile_data_complete(user):
        """ Validates User Profile Data """

        user_exists = db.session.query(User).filter_by(id=user.id).first()

        if user_exists:
            if (
                user_exists.gross_income_range is None
                or len(user_exists.gross_income_range) == 0 
                or user_exists.investment_amount is None 
                or len(user_exists.investment_risk) == 0
            ):
                return False
        else:
            return False

        return True


    @staticmethod
    def get_profile_data(user):
        """ Fetch User Profile Data """

        user_exists = db.session.query(User).filter_by(id=user.id).first()

        return User(
            id      = user_exists.id,
            email   = user_exists.email,
            name    = user_exists.name,
            gross_income_range  = user_exists.gross_income_range,
            investment_amount   = user_exists.investment_amount,
            investment_risk     = user_exists.investment_risk,
            is_admin              = user_exists.is_admin
        ) if user_exists else None

    @staticmethod
    def save_profile_data(user, gross_income_range, investment_amount, investment_risk):
        """ Save User Data """

        user_exists = db.session.query(User).filter_by(id=user.id).first()

        if user_exists:
            user_exists.gross_income_range = gross_income_range
            user_exists.investment_amount = investment_amount
            user_exists.investment_risk = ( 'low' if len(investment_risk) == 0 else investment_risk)

            db.session.commit()

            flash('Profile updated successfully!', 'success')
        else:
            flash('User not found.', 'error')

    @staticmethod
    def get(user):
        """" return User to Context """

        user_exists = db.session.query(User).filter_by(id=user).first()
        print(user_exists)
        return User(
            id      = user_exists.id,
            name    = user_exists.name,
            email   = user_exists.email,
            is_admin = user_exists.is_admin
        ) if user_exists else None

class LocalUser(UserMixin, db.Model):
    """ Local User Object """
    __tablename__ = 'local_user'
    id      = db.Column(db.Text, unique=True, primary_key=True)
    user_id = db.Column(db.Text, db.ForeignKey('user.id'))
    name    = db.Column(db.String(80), unique=True, nullable=False)
    email   = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)


    def verify(self):
        if User.query.filter_by(email=self.email).first():
            #raise ValidationError("Email registered!")
            flash("An account is already created using this email", "error")
            return False

        if User.query.filter_by(name=self.name).first():
            #raise ValidationError("Username already taken!")
            flash("Username already taken!", "error")
            return False
        return True

    def register(self, localuser):
        user_exists = (id == "")
        if(user_exists):
            # if already exists
            print('user exists')
        else:
            # assign the id for the new row
            localuser.id = str(randint(100000000000000000000, 1000000000000000000000))
            # add the local user
            db.session.add(localuser) 
        db.session.commit()   

class LocalUser_Login(FlaskForm):
    """ A class to login local users """
    username = StringField(
            validators = [
                InputRequired(),
                Length(3, 20, message="Validate Name"),
                Regexp(
                    "^[A-Za-z][A-Za-z0-9_.]*$",
                    0,
                    "Invalid username character detected"
                ),
            ]
        )
    password = PasswordField(validators=[InputRequired(), Length(8, 72)])
    def GetHashedPw(self):
        # does the username exist
        username = self.username.data.upper()
        userExists = db.session.query(LocalUser).filter_by(name=username).first()
        if(userExists):
            return userExists.password
        return None
    
    def Get_User(self):
        username = self.username.data.upper()
        return db.session.query(User).filter_by(name=username).first()

class CryptoList(db.Model):
    """ Model for the Crypto List Table """

    __tablename__ = 'crypto_list'

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code        = db.Column(db.Text, nullable=False)
    desc        = db.Column(db.Text)
    is_active   = db.Column(db.Boolean)
    code_AG     = db.Column(db.Text)
    code_CG     = db.Column(db.Text)
    code_FMP    = db.Column(db.Text)
    code_CRYPTO = db.Column(db.Text)
    id_CRYPTO   = db.Column(db.Text)

    def __repr__(self):
        return f'<CryptoList {self.code}>'
    
    @staticmethod
    def getList():
        return CryptoList.query.all()

    @staticmethod
    def _load_csv_file():
        """ Use this to protect access to the CSV File """
        _csvfile = "digital_currency_list.csv"

        transaction_session = db.session()
        transaction_session.execute(CryptoListLoadDataTransaction.get_query())

        if not os.path.exists(_csvfile):
            raise RuntimeError("Digital Currency File Does Not exists")

        with current_app.open_resource(_csvfile, "r") as f:
            reader = csv.reader(f, delimiter=',')
            next(reader)

            for row in reader:
                record_exists = transaction_session.query(CryptoList).filter_by(code=row[0]).count()

                if record_exists is None or record_exists <= 0:
                    sql = CryptoListLoadDataExec.get_query(first=row[0], second=row[1])
                    print(sql)
                    transaction_session.execute(
                        text(sql)
                    )

            transaction_session.execute(text("COMMIT"))

    @staticmethod
    def load_csv_data():
        """ public call to private load file """

        CryptoList._load_csv_file()
    @staticmethod
    def get_api_coin_id(coin_code, field_id):
        """" return Coin Id for a specify API """

        valid = {None, "code", "code_AG", "code_CG", "code_FMP", "id_CRYPTO"}
        if field_id not in valid:
            raise ValueError("results: field_id must be one of %r." % valid)
    
        db_proc = DatabaseGetCryptoCodeByAPI()
        return db_proc.execute_processing_query(coin_code, field_id)

    @staticmethod
    def get_active_coins():

        """" return active coins """
        return db.session.query(CryptoList).filter((CryptoList.is_active=='True' or CryptoList.is_active==1 or CryptoList.is_active==True)).all()


class AlphaVantageDcurrMonthly(db.Model):
    """ AlphaVantage Model """

    __tablename__ = 'alpha_vantage_dcurr_monthly'

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp   = db.Column(db.Date, nullable=False)
    open_cny    = db.Column(db.Float)
    high_cny    = db.Column(db.Float)
    low_cny     = db.Column(db.Float)
    close_cny   = db.Column(db.Float)
    open_usd    = db.Column(db.Float)
    high_usd    = db.Column(db.Float)
    low_usd     = db.Column(db.Float)
    close_usd   = db.Column(db.Float)
    volume      = db.Column(db.Float)
    market_cap_usd = db.Column(db.Float)

    __table_args__ = (UniqueConstraint('timestamp'),)

    def __repr__(self):
        return f'<AlphaVantageDcurrMonthly {self.timestamp}>'


class ApiFMPHistoricalPriceFull(db.Model):
    """ FMP Historical Data Table """

    __tablename__ = 'API_FMP_historical_price_full'

    id = db.Column(db.Integer, primary_key=True)
    coin = db.Column(db.Text, nullable=False)
    date = db.Column(db.Text, nullable=False)
    open = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    close = db.Column(db.Float)
    adjClose = db.Column(db.Float)
    volume = db.Column(db.Integer)
    unadjustedVolume = db.Column(db.Integer)
    change = db.Column(db.Float)
    changePercent = db.Column(db.Float)
    vwap = db.Column(db.Float)
    label = db.Column(db.Text)
    changeOverTime = db.Column(db.Float)

    def __repr__(self):
        return f'<ApiFMPHistoricalPriceFull {self.coin}, {self.date}>'

    @staticmethod
    def update_historical_data(records, coin):
        """ Update Database Risk Table """

        #clear table records only for this particular coin... there may be other in the table
        db.session.execute(text(f"DELETE FROM API_FMP_historical_price_full WHERE coin = '{coin}'"))

        db.session.commit()
        print(records)
        for record in records.json()["historical"]:
        
            db_proc = DatabaseRiskUpdate()
            db_proc.execute_processing_query(record, coin)
