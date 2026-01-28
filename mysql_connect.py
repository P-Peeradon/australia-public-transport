from sqlalchemy import create_engine
import pymysql

# 1. Define your credentials
user = "your_username"
password = "your_password"
host = "localhost" # or an IP address
port = "3306"
db_name = "mel_syd_adl_transport"

# 2. Create the engine
url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
engine = create_engine(url)

def connect_sql_analyse():
    try:
        with engine.connect() as connection:
            print("Successfully connected to MySQL!")
    except Exception as e:
        print(f"Connection failed: {e}")