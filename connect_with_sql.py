# mysql imports
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
from connect_with_mongoDB import store_data
import logging_file


def save_to_sql(user, password, data, table_name):
    global db_connection
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user=user,
            password=password
        )
        logging_file.info(f"connection established {mydb}")
    except Exception as e:
        logging_file.error(f"Exception in making connection with SQL {e}")
    mycursor = mydb.cursor()
    try:
        mycursor.execute("CREATE DATABASE IF NOT EXISTS youtube_scrapper")
        mycursor.execute("USE youtube_scrapper")
        mycursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    except Exception as e:
        logging_file.error(e)

    conn_str = f'mysql+pymysql://{user}:{password}@localhost:3306/youtube_scrapper'
    try:
        db_connection = create_engine(conn_str)
        print("connection with SQLAlchemy established")
        logging_file.info(db_connection)
    except Exception as e:
        logging_file.error(f"some error occurred with sqlalchemy {e}")

    try:
        df = pd.DataFrame(data)
        df.drop("comments", axis=1, inplace=True)
        df.to_sql(f"{table_name}", con=db_connection, index=False)
    except Exception as e:
        logging_file.error(f"Exception in DataFrame {e}")

