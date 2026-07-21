import json
import pymysql

class MenuRepo:
    """menu, order_log 테이블에 대한 쿼리를 담당한다.
    쿼리 자체를 db.lock으로 감싸 여러 클라이언트 스레드가 동시에
    같은 커넥션/커서를 건드리지 않도록 한다.
    """

    def __init__(self, db):
        self.db = db
        self.conn = db.conn
        self.cur = db.cur

    # (기존 food_court_menu 딕셔너리와 같은 모양을 유지해 broadcaster.send_menu가 그대로 동작)
    def get_menu(self):
        with self.db.lock:
            self.cur.execute(
                "SELECT category, name, price, image FROM menu ORDER BY category, id"
            )
            rows = self.cur.fetchall()

        menu = {}
        for row in rows:
            menu.setdefault(row["category"], []).append(
                {"name": row["name"], "price": row["price"], "image": row["image"]}
            )
        return menu

    def add_ordered_menu(self, order_log):
        with self.db.lock:
            try:
                self.cur.execute(
                    "INSERT INTO order_log (order_date, order_no, order_time, items) "
                    "VALUES (%s, %s, %s, %s)",
                    (
                        order_log["order_date"],
                        order_log["order_no"],
                        order_log["order_time"],
                        order_log["items"],
                    ),
                )
                self.conn.commit()
                return True
            except pymysql.err.IntegrityError:
                # (order_date, order_no) UNIQUE 위반 - 같은 날짜에 중복된 주문번호
                self.conn.rollback()
                return False

    def get_last_order_no(self, order_date):
        with self.db.lock:
            self.cur.execute(
                "SELECT MAX(order_no) AS max_no FROM order_log WHERE order_date = %s", (order_date,),
            )
            row = self.cur.fetchone()
            return row["max_no"] if row else None

    # /order_log 명령어에서 사용 - 전체 주문 기록 조회
    def get_ordered_menu(self):
        with self.db.lock:
            self.cur.execute(
                "SELECT order_date, order_no, order_time, items FROM order_log ORDER BY id"
            )
            rows = self.cur.fetchall()

        for row in rows:
            row["items"] = json.loads(row["items"])
        return rows
