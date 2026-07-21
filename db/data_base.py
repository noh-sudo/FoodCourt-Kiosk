import threading
import pymysql
from db_key import host, user, pw, database

class DataBase:
    def __init__(self):
        self.conn = pymysql.connect(
            host=host,
            user=user,
            password=pw,
            database=database,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.cur = self.conn.cursor()
        self.lock = threading.Lock()

    def close(self):
        self.cur.close()
        self.conn.close()
