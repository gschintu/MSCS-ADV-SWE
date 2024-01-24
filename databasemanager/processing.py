""" This is a module for statically returning Query Strings """

from databasemanager.database import db
from sqlalchemy.sql import text
from sqlalchemy.exc import ResourceClosedError

class DatabaseProcessing:
    """ Class to return static query strings """

    def __init__(self):
        self.db = db

    def get_query(self, *args, **kwargs):
        """ Method returning query string """

        raise NotImplementedError("Must be implemented by subclasses")

    # def execute_processing_query(self, *args, **kwargs):
    #     """ Execute the Query  """

    #     #cuser = kwargs.get('cuser')
    #     query = self.get_query(*args, **kwargs)

    #     # Using db.session.execute() to keep native SQL.
    #     # Future implementations can use SQLAlchemy ORM
    #     if isinstance(query, tuple):
    #         cursor = self.db.session.execute((query[0]), (query[1]))
    #     else:
    #         cursor = self.db.session.execute(text(query))

    #     self.db.session.commit()

    #     return cursor.fetchall()

    def execute_processing_query(self, *args, **kwargs):
        """ Execute the Query """
        query = self.get_query(*args, **kwargs)
        
        # Execute the query within the transaction
        if isinstance(query, tuple):
            result = self.db.session.execute(query[0], query[1])
        else:
            result = self.db.session.execute(text(query))

            # Commit the transaction explicitly
            self.db.session.commit()

        # Fetch the results after the transaction is committed
        try:
            # Only attempt to fetch rows if the statement is a SELECT statement
            if result.returns_rows:
                rows = result.fetchall()
                return rows
            else:
                # For non-SELECT statements, just return an empty list or None
                return []
        except ResourceClosedError as e:
            # Handle the specific case where result object does not return rows
            # If this is expected (e.g., for UPDATE, INSERT, DELETE), handle accordingly
            print("The query did not return any rows.")
            return []
        except Exception as e:
            # If fetching fails for any other reason, rollback and re-raise the exception
            self.db.session.rollback()
            raise
    
class DatabaseRisk(DatabaseProcessing):
    """ Static Query String for Risk """

    def get_query(self, *args, **kwargs):
        """ Risk Static Query """
        if len(args) == 1:
            user_id = args[0]
            print(f"user_id is {user_id} ")
        else:
            raise ValueError("Missing Positional Argument")

        return f'''
            WITH UserRisk AS (
            SELECT
                id,
                gross_income_range,
                investment_amount,
                investment_risk,
                CASE
                --low
                WHEN gross_income_range = '20' AND investment_risk = 'low' THEN 0.05
                WHEN gross_income_range = '50' AND investment_risk = 'low' THEN 0.1
                WHEN gross_income_range = '100' AND investment_risk = 'low' THEN 0.15
                WHEN gross_income_range = '150' AND investment_risk = 'low' THEN 0.20
                WHEN gross_income_range = '200' AND investment_risk = 'low' THEN 0.25
                WHEN gross_income_range = '200+' AND investment_risk = 'low' THEN 0.30
                --medium
                WHEN gross_income_range = '20' AND investment_risk = 'medium' THEN 0.15
                WHEN gross_income_range = '50' AND investment_risk = 'medium' THEN 0.20
                WHEN gross_income_range = '100' AND investment_risk = 'medium' THEN 0.25
                WHEN gross_income_range = '150' AND investment_risk = 'medium' THEN 0.30
                WHEN gross_income_range = '200' AND investment_risk = 'medium' THEN 0.35
                WHEN gross_income_range = '200+' AND investment_risk = 'medium' THEN 0.40
                --high
                WHEN gross_income_range = '20' AND investment_risk = 'high' THEN 0.20
                WHEN gross_income_range = '50' AND investment_risk = 'high' THEN 0.25
                WHEN gross_income_range = '100' AND investment_risk = 'high' THEN 0.30
                WHEN gross_income_range = '150' AND investment_risk = 'high' THEN 0.35
                WHEN gross_income_range = '200' AND investment_risk = 'high' THEN 0.40
                WHEN gross_income_range = '200+' AND investment_risk = 'high' THEN 0.45
                END AS max_risk_value
            FROM
                user
            ),
            CryptoTrend AS (
            SELECT
                coin,
                AVG(high) AS avg_price_high,
                AVG(low) AS avg_price_low,
                MIN(low) AS min_price_low,
                MAX(high) AS max_price_high,
                AVG(changePercent) AS avg_change_percent,
                AVG(changeOverTime) AS avg_change_over_time
            FROM
                API_FMP_historical_price_full
            GROUP BY
                coin
            )
            SELECT
            c.coin,
            FORMAT("%.2f%",(c.avg_change_percent * 100)) AS avg_change_percent,
            FORMAT("$%.2f",(c.avg_change_over_time * 100)) AS avg_change_over_time,
            ROUND(c.avg_price_low,2) AS avg_price_low,
            ROUND(c.avg_price_high,2) AS avg_price_high,
            ROUND(c.min_price_low,2) AS min_price_low,
            ROUND(c.max_price_high,2) AS max_price_high,

            u.id AS user_id,
            u.max_risk_value * 100 AS max_risk_value,
            FORMAT("$%.2f", (u.max_risk_value * u.investment_amount)) AS max_risk_investment,
            FORMAT("$%.2f", (c.avg_change_percent * u.investment_amount)) AS proper_risk_investment
            FROM
            CryptoTrend c
            JOIN
            UserRisk u
            WHERE
                (c.avg_change_percent BETWEEN u.max_risk_value * -1 AND u.max_risk_value)
                -- AND u.investment_amount * u.max_risk_value BETWEEN c.min_price_low AND c.max_price_high
             AND u.id = '{str(user_id)}'
            '''


class DatabaseHistoricalData(DatabaseProcessing):
    """ Static Query String for Historical Data """
    def get_query(self, *args, **kwargs):
        return '''
            SELECT
                coin,
                ROUND(AVG(high),2) AS avg_price_high,
                ROUND(AVG(low),2) AS avg_price_low,
                ROUND(MIN(low),2) AS min_price_low,
                ROUND(MAX(high),2) AS max_price_high,
                ROUND(AVG(changePercent),2) AS avg_change_percent,
                ROUND(AVG(changeOverTime),2) AS avg_change_over_time
            FROM
                API_FMP_historical_price_full
            GROUP BY
                coin
            '''

class DatabaseRiskUpdate(DatabaseProcessing):
    """ Static Query String for Risk """

    def get_query(self, *args, **kwargs):
        """ Risk Static Query """

       # record  = kwargs.get('record')
       # coin    = kwargs.get('coin')

        record, coin = args

       # print(f"coin in get query:{coin.code}")

        return f'''
            INSERT INTO API_FMP_historical_price_full (
                coin,
                date,
                open,
                high,
                low,
                close,
                adjClose,
                volume,
                unadjustedVolume,
                change,
                changePercent,
                vwap,
                label,
                changeOverTime
            ) VALUES (
                '{coin}', '{record['date']}', {record['open']},
                {record['high']}, {record['low']}, {record['close']},
                {record['adjClose']}, {record['volume']}, {record['unadjustedVolume']},
                {record['change']}, {record['changePercent']}, {record['vwap']},
                '{record['label']}', {record['changeOverTime']})'''

class DatabaseCryptoList(DatabaseProcessing):
    """ Static Query String for Listing Crypto """

    def get_query(self, *args, **kwargs):
        return ''' SELECT * FROM crypto_list '''


class DatabaseUserList(DatabaseProcessing):
    """ Static Query for Listing Users """

    def get_query(self, *args, **kwargs):
        return '''SELECT * FROM user'''


class DatabaseUpdateCrypto(DatabaseProcessing):
    """ Non Static Query to Update Crypto """

    def get_query(self, *args, **kwargs):
        if len(args) == 3:
            column, newrecord, recordid = args
        else:
            raise ValueError("Three positional arguments are required")

        if column is not None and newrecord is not None and recordid is not None:
            return f"UPDATE crypto_list SET {column} = '{newrecord}' WHERE id = {recordid}"

        raise ValueError("Missing positional argument(s)")


class DatabaseCryptoUpdatedResults(DatabaseProcessing):
    """ Non static Query to Retrieve Updated Results """

    def get_query(self, *args, **kwargs):
        if len(args) == 1:
            recordid = args[0]
        else:
            raise ValueError("Missing Positional Argument")

        if recordid is not None:
            return f"SELECT * FROM crypto_list WHERE id = {recordid}"

class DatabaseGetCryptoCodeByAPI(DatabaseProcessing):
    """ Non Static Query to Retrieve Crypto Code for a specific API """

    def get_query(self, *args, **kwargs):
        if len(args) == 2:
            coin_code, field_id = args
        else:
            raise ValueError("Three positional arguments are required")

        if field_id is not None and coin_code is not None:
            return f"SELECT {field_id} AS code_ret FROM crypto_list WHERE code = '{coin_code}'"

        raise ValueError("Missing positional argument(s)")
    
class CryptoListLoadDataTransaction(DatabaseProcessing):
    """ Begin Transaction """

    @classmethod
    def get_query(cls, *args, **kwargs):
        """ Begin Transaction """

        return text("BEGIN TRANSACTION")


class CryptoListLoadDataExec():
    """ Load Crypto Data From CSV File """

    @classmethod
    def get_query(cls, *args, **kwargs):
        """ Return a Query String to Update Crypto List """

        value_one = kwargs.get('first')
        value_two = kwargs.get('second')

        return f"INSERT INTO crypto_list (code, [desc]) VALUES ('{value_one}', '{value_two}')"

class DatabaseUpdateUser(DatabaseProcessing):
    """ Non Static Query to Update User based on Column field """

    def get_query(self, *args, **kwargs):
        print(f"len args = {len(args)}")
        if len(args) == 3:
            column, newrecord, recordid = args
        else:
            raise ValueError("Three positional arguments are required")

        if column is not None and newrecord is not None and recordid is not None:
            return f"UPDATE user SET {column} = '{newrecord}' WHERE id = '{recordid}'"
        raise ValueError("Missing positional argument(s)")