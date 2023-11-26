from sqlalchemy import create_engine

# Replace the following with your actual database credentials
username = 'postgres'
password = ''
host = 'localhost'
port = '5432'
database = 'postgres'

# Create the connection string
connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"

# Create an engine
engine = create_engine(connection_string)

# Connect to the database
db = engine.connect()
