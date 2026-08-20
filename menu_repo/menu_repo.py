import json
import mysql.connector

class MenuRepo:
    """menu, order_log 테이블에 대한 쿼리를 담당한다.
    쿼리마다 db 커넥션 풀에서 커넥션을 빌리고, 사용이 끝나면
    커서와 커넥션을 모두 풀에 반환한다.
    """

    def __init__(self, db):
        self.db = db

    # (기존 food_court_menu 딕셔너리와 같은 모양을 유지해 broadcaster.send_menu가 그대로 동작)
    def get_menu(self):
        conn = self.db.get_connection()
        try:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    "SELECT category, name, price, image FROM menu ORDER BY category, id"
                )
                rows = cur.fetchall()
            finally:
                cur.close()
        finally:
            conn.close()

        menu = {}
        for row in rows:
            menu.setdefault(row["category"], []).append(
                {"name": row["name"], "price": row["price"], "image": row["image"]}
            )
        return menu

    def add_ordered_menu(self, order_log):
        conn = self.db.get_connection()
        try:
            cur = conn.cursor(dictionary=True)
            try:
                try:
                    cur.execute(
                        "INSERT INTO order_log (order_date, order_no, order_time, items) "
                        "VALUES (%s, %s, %s, %s)",
                        (
                            order_log["order_date"],
                            order_log["order_no"],
                            order_log["order_time"],
                            order_log["items"],
                        ),
                    )
                    conn.commit()
                    return True
                except mysql.connector.errors.IntegrityError:
                    # (order_date, order_no) UNIQUE 위반 - 같은 날짜에 중복된 주문번호
                    conn.rollback()
                    return False
            finally:
                cur.close()
        finally:
            conn.close()

    def get_last_order_no(self, order_date):
        conn = self.db.get_connection()
        try:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    "SELECT MAX(order_no) AS max_no FROM order_log WHERE order_date = %s", (order_date,),
                )
                row = cur.fetchone()
                return row["max_no"] if row else None
            finally:
                cur.close()
        finally:
            conn.close()

    # /order_log 명령어에서 사용 - 전체 주문 기록 조회
    def get_ordered_menu(self):
        conn = self.db.get_connection()
        try:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(
                    "SELECT order_date, order_no, order_time, items FROM order_log ORDER BY id"
                )
                rows = cur.fetchall()
            finally:
                cur.close()
        finally:
            conn.close()

        for row in rows:
            row["items"] = json.loads(row["items"])
        return rows
