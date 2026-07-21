import threading
import pymysql

class DataBase:
    def __init__(self):
        self.conn = pymysql.connect(
            host="localhost",
            user="root",
            password="1234",
            database="kiosk",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.cur = self.conn.cursor()
        self.lock = threading.Lock()

    def close(self):
        self.cur.close()
        self.conn.close()
