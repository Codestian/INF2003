from sqlalchemy import text

def create_tables(db):
    users_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        userid SERIAL PRIMARY KEY,
        email VARCHAR(128) UNIQUE NOT NULL,
        username VARCHAR(64) NOT NULL,
        password VARCHAR(256) NOT NULL
    );
    """

    transaction_type_table_sql = """
    CREATE TABLE IF NOT EXISTS transaction  (
        transactionid SERIAL PRIMARY KEY,
        type VARCHAR(64) NOT NULL,
        category VARCHAR(64)
    );
    """

    frequency_table_sql = """
    CREATE TABLE IF NOT EXISTS frequency (
        freqid SERIAL PRIMARY KEY,
        freqtype VARCHAR(64) NOT NULL
    );
    """

    income_table_sql = """
    CREATE TABLE IF NOT EXISTS income (
        incomeid SERIAL PRIMARY KEY,
        name VARCHAR(64) NOT NULL,
        value FLOAT NOT NULL,
        transactionid INTEGER REFERENCES transaction(transactionid),
        datepurchased TIMESTAMP,
        userid INTEGER REFERENCES users(userid),
        freqid INTEGER REFERENCES frequency(freqid),
        nextdue TIMESTAMP
    );
    """

    expense_table_sql = """
    CREATE TABLE IF NOT EXISTS expenses (
        expenseId SERIAL PRIMARY KEY,
        name VARCHAR(64) NOT NULL,
        value FLOAT NOT NULL,
        transactionid INTEGER REFERENCES transaction(transactionid),
        datepurchased TIMESTAMP,
        userid INTEGER REFERENCES users(userid),
        frequency INTEGER REFERENCES frequency(freqid),
        nextdue TIMESTAMP
    );
    """

    asset_table_sql = """
    CREATE TABLE IF NOT EXISTS assets (
        assetid SERIAL PRIMARY KEY,
        name VARCHAR(64) NOT NULL,
        value FLOAT NOT NULL,
        amount FLOAT NOT NULL,
        assettypeid INTEGER REFERENCES assettype(assettypeid),
        datepurchased TIMESTAMP,
        userid INTEGER REFERENCES users(userid),
        purchaseprice FLOAT NOT NULL
    );
    """

    asset_type_table_sql = """
    CREATE TABLE assettype (
        assettypeid SERIAL PRIMARY KEY,
        type VARCHAR(64) NOT NULL
    );
    """
    filter_by_highest_value_asset = """
    SELECT *
    FROM assets
    ORDER BY value DESC
    ;
    """
    filter_by_highest_return = """
    SELECT *
    FROM assets
    ORDER BY (value - purchaseprice) DESC;
"""
    filter_by_alphabetical = """
    SELECT *
    FROM assets
    ORDER BY name;"""

    update_next_due_by_frequency_type = """
    UPDATE income
    SET nextdue = (SELECT DATE(nextdue,  (SELECT freqtype FROM frequency WHERE frequency.freqid = income.freqid)))
    WHERE date(nextdue) = date('now');"""
    filter_by_nearest_due_income = """
    SELECT *
    FROM income
    ORDER BY nextdue ASC"""
    filter_by_nearest_due_expenses = """
    SELECT *
    FROM income
    ORDER BY nextdue ASC
    """
    most_recently_added = """
    WITH recent_add AS (
    SELECT 'income' AS category, name, value, datepurchased 
    FROM income
    WHERE datepurchased = (SELECT MAX(datepurchased ) FROM income)

    UNION ALL

    SELECT 'expenses' AS category, name, value, datepurchased
    FROM expenses
    WHERE datepurchased = (SELECT MAX(datepurchased) FROM expenses)

    UNION ALL

    SELECT 'assets' AS category, name, value, date
    FROM assets
    WHERE date= (SELECT MAX(date) FROM assets)
)

SELECT category, name, value, datepurchased
FROM recent_add
ORDER BY datepurchased DESC
"""
    overall_portfolio_value = """
    SELECT SUM(value * amount) AS total_value
    FROM assets;
    """
    overall_distribution_of_portfolio = """
    SELECT
  a.assettypeid,
  at.type,
  SUM(value * amount) AS total_value,
  (SUM(value * amount) / SUM(value * amount) OVER ()) * 100 AS percentage
FROM
  assets a
JOIN
  assettype at ON a.assettypeid = at.assettypeid
GROUP BY
  a.assettypeid, at.type;
     """
    overall_distribution_of_income = """
   SELECT
  i.transactionid,
  tr.type AS category,
  SUM(i.value) AS total_value
FROM
  income i
JOIN
  transactions tr ON i.transactionid = tr.transactionid
GROUP BY
  i.transactionid, tr.type;
;
"""
    overall_distribution_of_expenses = """
   SELECT
  e.transactionid,
  tr.type AS category,
  SUM(e.value) AS total_value
FROM
  expenses e
JOIN
  transactions tr ON e.transactionid = tr.transactionid
GROUP BY
  e.transactionid, tr.type;
"""
    
    sql_statements = [
        users_table_sql,
        transaction_type_table_sql,
        frequency_table_sql,
        asset_type_table_sql,
        asset_table_sql,
        income_table_sql,
        expense_table_sql,
        filter_by_highest_value_asset,
        filter_by_highest_return,
        filter_by_alphabetical,
        update_next_due_by_frequency_type,
        filter_by_nearest_due_income,
        filter_by_nearest_due_expenses,
        most_recently_added,
        overall_portfolio_value,
        overall_distribution_of_portfolio,
        overall_distribution_of_income,
        overall_distribution_of_expenses,
        predict_income_expenses,
    ]

    # Execute SQL statements
    with db.engine.connect() as conn:
        for sql in sql_statements:
            conn.execute(text(sql))
            conn.commit()
