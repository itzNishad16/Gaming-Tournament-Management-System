import os

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection

load_dotenv()


def get_connection() -> MySQLConnection:
    """Create and return a MySQL connection to gaming_tournament_db."""
    password = os.getenv("MYSQL_PASSWORD")
    if password is None:
        raise ValueError("MYSQL_PASSWORD environment variable is not set.")

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=password,
            database="gaming_tournament_db",
        )
        return connection
    except Error as exc:
        raise ConnectionError(f"Could not connect to MySQL: {exc}") from exc


def test_connection() -> None:
    """Try opening a connection and print whether it worked."""
    connection = None
    try:
        connection = get_connection()
        if connection.is_connected():
            print("Database connection successful.")
        else:
            print("Database connection failed: connection was not established.")
    except Exception as exc:
        print(f"Database connection failed: {exc}")
    finally:
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    test_connection()
