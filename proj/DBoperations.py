import sqlite3
from userclass import User
from datetime import datetime
from dateutil.relativedelta import relativedelta
DATABASE = 'test.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    return conn

def register_user(email, username, password):
    conn = get_db_connection()
    cur = conn.cursor()

    # Check if the email already exists
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return "User already exists with this email."

    # Insert new user
    cur.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", 
                (email, username, password))
    conn.commit()
    cur.close()
    conn.close()
    return "User registered successfully."

def valid_login(email,password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = cur.fetchone()
    conn.close()

    if user:
        return True
    else:
        return False
    
def retrieve_userdata(email):        
        conn= get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users where email = ?",(email,))
        user = cur.fetchone()
        conn.close()
        curuser =  User(user_id=user[0],email=user[1],name=user[2])
        return  curuser

def get_assets_for_user(userid):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            assetid, 
            name, 
            value, 
            amount, 
            assettypeid, 
            date, 
            userid, 
            purchaseprice,
            value * amount AS total_value, 
            ((value * amount) - (purchaseprice * amount)) / (purchaseprice * amount) * 100 AS profit_percentage
        FROM 
            assets
        WHERE 
            userid = ?;
    """, (userid,))

    assets = cur.fetchall()
    conn.close()
    return assets
def filter_highest_assets(userid):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT 
            assetid, 
            name, 
            value, 
            amount, 
            assettypeid, 
            date, 
            userid, 
            purchaseprice,
            value * amount AS total_value, 
            ((value * amount) - (purchaseprice * amount)) / (purchaseprice * amount) * 100 AS profit_percentage
        FROM 
            assets
        WHERE 
            userid = ?
        ORDER BY (value - purchaseprice) DESC
    """, (userid,))

    assets1 = cur.fetchall()
    conn.close()
    return assets1
def overall_portfolio_value(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""SELECT SUM(value * amount) AS total_value
    FROM assets
    WHERE userid = ?""", (user_id,))
    data = cur.fetchall()
    conn.close()
    return data

def delete_user(email):
    conn= get_db_connection()
    cur=conn.cursor()
    cur.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()
    cur.close()
    conn.close()

def add_new_asset(name, value, amount, asset_type_id, date, user_id, purchase_price):
    conn = get_db_connection()
    cur = conn.cursor()

    # Convert amount and purchase_price to float
    amount = float(amount)
    purchase_price = float(purchase_price)

    # Check if the asset already exists
    cur.execute("""
        SELECT amount, purchaseprice FROM assets 
        WHERE name = ? AND assettypeid = ? AND userid = ?
    """, (name, asset_type_id, user_id))

    existing_asset = cur.fetchone()

    if existing_asset:
        # Asset exists, calculate new amount and average purchase price
        old_amount, old_purchase_price = existing_asset
        new_amount = old_amount + amount
        new_purchase_price = ((old_purchase_price * old_amount) + (purchase_price * amount)) / new_amount

        # Update the existing asset
        cur.execute("""
            UPDATE assets 
            SET amount = ?, purchaseprice = ?, date = ?
            WHERE name = ? AND assettypeid = ? AND userid = ?
        """, (new_amount, new_purchase_price, date, name, asset_type_id, user_id))
    else:
        # Asset does not exist, insert a new one
        cur.execute("""
            INSERT INTO assets (name, value, amount, assettypeid, date, userid, purchaseprice)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, value, amount, asset_type_id, date, user_id, purchase_price))

    conn.commit()
    cur.close()
    conn.close()


def delete_asset(asset_id):
    conn = get_db_connection()  # Make sure this function returns a database connection
    cur = conn.cursor()

    # Execute the DELETE statement
    cur.execute("DELETE FROM assets WHERE assetid = ?", (asset_id,))

    conn.commit()
    cur.close()
    conn.close()



def get_all_incomes(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            i.incomeid,
            i.name, 
            t.type, 
            i.value, 
            i.datepurchased, 
            f.freqtype, 
            i.nextdue
        FROM 
            income i
        JOIN 
            frequency f ON i.freqid = f.freqid
        JOIN 
            transactions t ON i.transactionid = t.transactionid
        WHERE 
            i.userid = ?;
    """, (user_id,))
    
    incomes = []
    for record in cur.fetchall():
        
        total_earned = calculate_total(record[3], record[4], record[5])
        incomes.append(record + (total_earned,))

    conn.close()
    print(incomes)
    return incomes

def printallincome():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("delete from income")
    transactions = cur.fetchall()
    conn.close()
    return transactions

def calculate_total(value, date_purchased_str, frequency):
    date_purchased = datetime.strptime(date_purchased_str, '%Y-%m-%d')
    current_date = datetime.now()

    if frequency == 'Daily':
        days_passed = (current_date - date_purchased).days
        return days_passed * value
    elif frequency == 'Weekly':
        weeks_passed = (current_date - date_purchased).days // 7
        return weeks_passed * value
    elif frequency == 'Monthly':
        months_passed = relativedelta(current_date, date_purchased).months + \
                        relativedelta(current_date, date_purchased).years * 12
        return months_passed * value
    elif frequency == 'Yearly':
        years_passed = relativedelta(current_date, date_purchased).years
        return years_passed * value
    

    return 0

def get_all_expenses(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            e.expenseId,
            e.name, 
            t.type, 
            e.value, 
            e.datepurchased, 
            f.freqtype, 
            e.nextdue
        FROM 
            expenses e
        JOIN 
            frequency f ON e.frequency = f.freqid
        JOIN 
            transactions t ON e.transactionid = t.transactionid
        WHERE 
            e.userid = ?;
    """, (user_id,))
    
    expenses = []
    for record in cur.fetchall():
        total_spent = calculate_total(record[3], record[4], record[5])
        expenses.append(record + (total_spent,))

    conn.close()
    return expenses

def get_transaction_types(category):
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch transaction types based on the category
    cur.execute("SELECT transactionid, type FROM transactions WHERE category = ?", (category,))
    
    transaction_types = [{'id': row[0], 'type': row[1]} for row in cur.fetchall()]
    
    conn.close()
    return transaction_types
def get_frequencies():
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch all frequencies
    cur.execute("SELECT freqid, freqtype FROM frequency")
    
    frequencies = [{'id': row[0], 'freqtype': row[1]} for row in cur.fetchall()]
    
    conn.close()
    return frequencies

def add_income(name, value, type_name, date_purchased,userid, frequency_name, next_due):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Resolve type_name to type_id
        cur.execute("SELECT transactionid FROM transactions WHERE type = ? AND category = 'income'", (type_name,))
        type_result = cur.fetchone()
        if type_result is None:
            raise ValueError(f"Income type '{type_name}' not found.")
        type_id = type_result[0]

        # Resolve frequency_name to frequency_id
        cur.execute("SELECT freqid FROM frequency WHERE freqtype = ?", (frequency_name,))
        frequency_result = cur.fetchone()
        if frequency_result is None:
            raise ValueError(f"Frequency type '{frequency_name}' not found.")
        frequency_id = frequency_result[0]

        # Now insert the income with the resolved IDs
        cur.execute("""
            INSERT INTO income (name, value, transactionid, datepurchased,userid, freqid, nextdue)
            VALUES (?, ?, ?, ?,?, ?, ?)
        """, (name, float(value), type_id, date_purchased,userid, frequency_id, next_due))

        conn.commit()
    except sqlite3.DatabaseError as e:
        # If a database operation fails, we roll back the transaction.
        conn.rollback()
        print(f"A database error occurred: {e}")
        raise
    except Exception as e:
        # For any other kind of exception, we just print and re-raise.
        print(f"An error occurred: {e}")
        raise
    finally:
        # Close the cursor and the connection.
        cur.close()
        conn.close()

    print("Income added successfully.")

def add_expense(name, value, type_name, date_purchased, userid, frequency_name, next_due):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Resolve type_name to type_id for expenses
        cur.execute("SELECT transactionid FROM transactions WHERE type = ? AND category = 'expense'", (type_name,))
        type_result = cur.fetchone()
        if type_result is None:
            raise ValueError(f"Expense type '{type_name}' not found.")
        type_id = type_result[0]

        # Resolve frequency_name to frequency_id
        cur.execute("SELECT freqid FROM frequency WHERE freqtype = ?", (frequency_name,))
        frequency_result = cur.fetchone()
        if frequency_result is None:
            raise ValueError(f"Frequency type '{frequency_name}' not found.")
        frequency_id = frequency_result[0]

        # Insert the expense with the resolved IDs
        cur.execute("""
            INSERT INTO expenses (name, value, transactionid, datepurchased, userid, frequency, nextdue)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, float(value), type_id, date_purchased, userid, frequency_id, next_due))

        conn.commit()
    except sqlite3.DatabaseError as e:
        conn.rollback()
        print(f"A database error occurred: {e}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    print("Expense added successfully.")


def delete_income(incomeid):
    conn = get_db_connection()  # Make sure this function returns a database connection
    cur = conn.cursor()

    # Execute the DELETE statement
    cur.execute("DELETE FROM income WHERE incomeid = ?", (incomeid,))

    conn.commit()
    cur.close()
    conn.close()

def delete_expense(expenseid):
    conn = get_db_connection()  # Make sure this function returns a database connection
    cur = conn.cursor()

    # Execute the DELETE statement
    cur.execute("DELETE FROM expenses WHERE expenseId = ?", (expenseid,))

    conn.commit()
    cur.close()
    conn.close()


def delete_tables():
    conn=get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()

    for table in tables:
        cur.execute(f"DROP TABLE {table[0]}")

    conn.commit()
    conn.close()

def create_tables():
    conn=get_db_connection()
    c =conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            userid INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(128) UNIQUE NOT NULL,
            username VARCHAR(64) NOT NULL,
            password VARCHAR(256) NOT NULL
        );
        """)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            transactionid INTEGER PRIMARY KEY AUTOINCREMENT,
            type VARCHAR(64) NOT NULL,
            category VARCHAR(64)
        );
        """)

    c.execute(
    """
        CREATE TABLE IF NOT EXISTS frequency (
            freqid INTEGER PRIMARY KEY AUTOINCREMENT,
            freqtype VARCHAR(64) NOT NULL
        );
        """)
    c.execute(
    """
        CREATE TABLE IF NOT EXISTS income (
            incomeid INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(64) NOT NULL,
            value FLOAT NOT NULL,
            transactionid INTEGER REFERENCES transactions(transactionid),
            datepurchased TIMESTAMP,
            userid INTEGER REFERENCES users(userid),
            freqid INTEGER REFERENCES frequency(freqid),
            nextdue TIMESTAMP
        );
        """)
    c.execute(
    """
        CREATE TABLE IF NOT EXISTS expenses (
            expenseId INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(64) NOT NULL,
            value FLOAT NOT NULL,
            transactionid INTEGER REFERENCES transactions(transactionid),
            datepurchased TIMESTAMP,
            userid INTEGER REFERENCES users(userid),
            frequency INTEGER REFERENCES frequency(freqid),
            nextdue TIMESTAMP
        );
        """)
    c.execute(
    """
        CREATE TABLE IF NOT EXISTS assets (
            assetid INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(64) NOT NULL,
            value FLOAT NOT NULL,
            amount FLOAT NOT NULL,
            assettypeid INTEGER REFERENCES assettype(assettypeid),
            date TIMESTAMP,
            userid INTEGER REFERENCES users(userid),
            purchaseprice FLOAT NOT NULL
        );
        """)
    c.execute(
    """
        CREATE TABLE IF NOT EXISTS assettype (
            assettypeid INTEGER PRIMARY KEY AUTOINCREMENT,
            type VARCHAR(64) NOT NULL
        );
        """)
def populate_tables():
    conn = get_db_connection()
    cur = conn.cursor()

    # Queries to populate assettype table
    asset_types = ['crypto', 'stocks']
    for asset_type in asset_types:
        cur.execute("INSERT INTO assettype (type) VALUES (?)", (asset_type,))

    # Queries to populate frequency table
    frequencies = ['Yearly', 'Monthly', 'Weekly', 'Daily']
    for frequency in frequencies:
        cur.execute("INSERT INTO frequency (freqtype) VALUES (?)", (frequency,))

    conn.commit()
    cur.close()
    conn.close()
def insert_transaction_types():
    conn= get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO transactions (type, category) VALUES 
    ('Rental', 'income'),
    ('Salary', 'income'),
    ('Dividends', 'income'),
    ('Rental', 'expense'),
    ('Utilities', 'expense'),
    ('Phone Bill', 'expense'),
    ('Insurance', 'expense');
    """)

    conn.commit()
    cur.close()
    conn.close()

def predict_income_expenses(userid):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        WITH predict_data AS (
            SELECT
                nextdue,
                SUM(value) AS net_value
            FROM
                (
                SELECT
                    nextdue,
                    value
                FROM
                    income
                WHERE
                    userid = ?

                UNION ALL

                SELECT
                    nextdue,
                    -value
                FROM
                    expenses
                WHERE
                    userid = ?
                ) AS combined
            GROUP BY
                nextdue
        )

        SELECT
            nextdue,
            SUM(net_value) OVER (ORDER BY nextdue) AS running_net_value
        FROM
            predict_data
        WHERE
            CAST(STRFTIME("%m", nextdue) AS INTEGER) = (
                SELECT
                CAST(STRFTIME("%m", MIN(nextdue)) AS INTEGER)
                FROM
                predict_data)
        ORDER BY
            nextdue
    """, (userid, userid))

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def overall_distribution_of_expenses(userid):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            e.transactionid,
            tr.type AS category,
            SUM(e.value) AS total_value
        FROM
            expenses e
        JOIN
            transactions tr ON e.transactionid = tr.transactionid
        WHERE
            e.userid = ?
        GROUP BY
            e.transactionid, tr.type;
    """, (userid,))

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def overall_distribution_of_income(userid):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            i.transactionid,
            tr.type AS category,
            SUM(i.value) AS total_value
        FROM
            income i
        JOIN
            transactions tr ON i.transactionid = tr.transactionid
        WHERE
            i.userid = ?
        GROUP BY
            i.transactionid, tr.type;
    """, (userid,))

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def overall_distribution_of_portfolio(userid):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            a.assettypeid,
            at.type,
            SUM(value * amount) AS total_value,
            (SUM(value * amount) / SUM(value * amount) OVER ()) * 100 AS percentage
        FROM
            assets a
        JOIN
            assettype at ON a.assettypeid = at.assettypeid
        WHERE
            a.userid = ?
        GROUP BY
            a.assettypeid, at.type;
    """, (userid,))

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def most_recently_added(userid):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        WITH recent_add AS (
            SELECT 'income' AS category, name, value, datepurchased 
            FROM income
            WHERE userid = ? AND datepurchased = (SELECT MAX(datepurchased ) FROM income WHERE userid = ?)

            UNION ALL

            SELECT 'expenses' AS category, name, value, datepurchased
            FROM expenses
            WHERE userid = ? AND datepurchased = (SELECT MAX(datepurchased) FROM expenses WHERE userid = ?)

            UNION ALL

            SELECT 'assets' AS category, name, value, date
            FROM assets
            WHERE userid = ? AND date = (SELECT MAX(date) FROM assets WHERE userid = ?)
        )

        SELECT category, name, value, datepurchased
        FROM recent_add
        ORDER BY datepurchased DESC
    """, (userid, userid, userid, userid, userid, userid))

    data = cur.fetchall()
    cur.close()
    conn.close()
    return data
