from mysql.connector import pooling
from db_key import host, user, pw, database

class DataBase:
    def __init__(self):
        self.pool = pooling.MySQLConnectionPool(
            pool_name="menu_pool",
            pool_size=5,
            host=host,
            user=user,
            password=pw,
            database=database,
            charset="utf8mb4",
        )

    def get_connection(self):
        return self.pool.get_connection()
