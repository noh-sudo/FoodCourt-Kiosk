import json
from datetime import datetime


class MenuModel:
    """menu_repo를 통해 메뉴 조회 / 주문 기록 저장을 담당한다.

    기존(in-memory) 버전과 동일한 인터페이스(get_menu, save_ordered_menu,
    show_ordered_menu)를 유지해서 broadcaster / order_router / server 쪽
    호출부는 수정 없이 그대로 동작한다.
    """

    def __init__(self, menu_repo):
        self.menu_repo = menu_repo

    # 메뉴 딕셔너리 호출 메서드
    def get_menu(self):
        return self.menu_repo.get_menu()

    def get_last_order_no(self, order_date):
        last_order_no = self.menu_repo.get_last_order_no(order_date)
        return last_order_no or 0

    # order_router._handle_order에서 호출
    # order_log = {"order_date": "...", "order_time": "...", "order_no": str(current_no), "items": [...]}
    def save_ordered_menu(self, order_log):
        order_no = order_log["order_no"]

        record = {
            "order_no": int(order_no),
            # 날짜/시각 판단은 order_router 책임 - 없으면 저장 시점으로 대체
            "order_date": order_log.get("order_date") or datetime.now().strftime("%Y-%m-%d"),
            "order_time": order_log.get("order_time") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            # MySQL JSON 컬럼에 넣기 위해 문자열로 직렬화
            "items": json.dumps(order_log.get("items", []), ensure_ascii=False),
        }

        success = self.menu_repo.add_ordered_menu(record)
        if not success:
            print(f"[system] 주문번호 {order_no} 중복 - 저장 실패")
        return success

    # 메인 스레드 명령어 /order_log
    def show_ordered_menu(self):
        orders = self.menu_repo.get_ordered_menu()
        if not orders:
            print("[system] 주문 기록이 없습니다.")
            return
        for order in orders:
            print(order)
