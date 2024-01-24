""" Database Utility functions """

import csv
import click
import sqlite3

# Flask imports
from flask import current_app, g
from flask.cli import with_appcontext

# Database Import
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

bcrypt  = Bcrypt()
migrate = Migrate()
db      = SQLAlchemy()

def retrieve_database():
    """ Retrieve the Database """

    if "db" not in g:
        g.db = sqlite3.connect(
            "sqlite_db", detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    """ Close the Database Connection """

    data = g.pop("db", None)

    if data is not None:
        data.close()


def load_csv_data():
    """ Load CSV Data """

    data = retrieve_database()
    try:
        with current_app.open_resource("digital_currency_list.csv", "r") as f:
            reader = csv.reader(f, delimiter=',')
            next(reader)  # Skip the header row

            # Start a transaction
            data.execute("BEGIN TRANSACTION")

            row_count = 0  # Initialize the counter
            for row in reader:

                rec_exists = data.execute("SELECT COUNT(*) AS how_many FROM crypto_list WHERE code = ?", (row[0],)).fetchone()
                if rec_exists[0] == None or rec_exists[0] <= 0:
                    data.execute(
                        "INSERT INTO crypto_list (code, [desc]) VALUES (?, ?)", (row[0], row[1])
                    )
                    row_count += 1  # Increment the counter for each row

            # Commit the transaction
            data.execute("COMMIT")

            print(f"{row_count} rows have been loaded from the CSV file.")
    except IOError:
        print("Error: File 'digital_currency_list.csv' not found!")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        # If there's any error, rollback the transaction
        data.execute("ROLLBACK")


def get_api_coin_id(coin_code, field_id):
    """ this is used by Downloader API classes """

    valid = {None, "code", "code_AG", "code_CG", "code_FMP"}
    if field_id not in valid:
        raise ValueError("results: field_id must be one of %r." % valid)

    coin_code_ret = None
    data = retrieve_database()

    if field_id is None:
        field_id= "code"
    try:
        crypto_data = data.execute (
            f"SELECT {field_id} AS code_ret FROM crypto_list WHERE code = ?", (str(coin_code),)
        )
        
        coin_rec = crypto_data.fetchone()

        if coin_rec is not None and coin_rec[0] is not None:
            coin_code_ret = coin_rec[0]

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    return coin_code_ret


def get_active_coins():
    """ this is used by Download Endpoints """

    # Assuming you have a SQLite database, connect to it
    conn = retrieve_database()
    cursor = conn.cursor()

    # Retrieve all active coins
    cursor.execute("SELECT code FROM crypto_list WHERE is_active = 1")
    active_coins = cursor.fetchall()

    # Extract coin codes from the query result
    return [coin[0] for coin in active_coins]


# def initialize():
#     """ Init DB """

#     data = retrieve_database()

#     with current_app.open_resource("schema.sql") as f:
#         data.executescript(f.read().decode("utf8"))


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""

    initialize()
    click.echo("Database Created.")


def init_app(app):
    """ Initialize application """

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
