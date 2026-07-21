"""수신된 메시지의 type에 따라 등록/주문/완료 처리를 담당
handle_client(소켓 송수신 루프)는 이 클래스에 메시지 처리를 위임,
소켓 읽기/쓰기 흐름 자체에만 집중한다.
"""
import threading
import datetime


class OrderRouter:
    def __init__(self, protocol, client_registry, broadcaster, menu_model):
        self.protocol = protocol
        self.client_registry = client_registry
        self.broadcaster = broadcaster
        self.menu_model = menu_model
        # 마지막으로 주문을 처리한 날짜 - 이 날짜와 오늘이 다르면 order_no를 1부터 다시 시작
        self.current_date = datetime.date.today()
        self.order_no = self.menu_model.get_last_order_no(self.current_date.strftime("%Y-%m-%d"))
        # 여러 order 클라이언트 스레드가 동시에 _handle_order를 호출해도
        # order_no 증가 + 방송 + 응답 구간이 하나의 원자적 단위로 처리되도록 보장
        self.order_lock = threading.Lock()
    def handle_message(self, client_socket, client_address, message, client_type):
        """메시지 하나를 처리한다.

        Returns:
            (client_type, exit_requested) 튜플
            client_type: 클라이언트 타입
            exit_requested: 이 연결을 종료해야 하면 True
        """
        address_text = str(client_address)
        msg_type = message.get("type")

        # 아직 client_type을 보내지 않은 클라이언트는 client_type/exit 메시지만 허용
        if msg_type != "client_type" and msg_type != "exit" and client_type is None:
            # self.send_error(client_socket, "먼저 클라이언트 타입을 보내주세요")
            return client_type, False

        if msg_type == "exit":
            print(f"{address_text} 접속 종료")
            # 클라이언트 측 타입 exit시 해당 클라이언트 루프 탈출, 종료
            return client_type, True

        # 주문, 주방, 전광판 클라이언트 구분
        if msg_type == "client_type":
            return self._handle_client_type(client_socket, client_address, message)

        # 주문측에서 보낸 메시지
        elif msg_type == "order":
            self._handle_order(client_socket, message)
            return client_type, False

        # 주방측에서 보낸 메시지
        elif msg_type == "order_complete":
            self._handle_order_complete(message)
            return client_type, False

        # 해당하는 msg_type 없을때
        else:
            print(f"[system] 메시지 타입 : {msg_type} 확인 불가")
            # self.send_error(client_socket, f"메시지 타입 : {msg_type} 확인 불가")
            return client_type, False

    def _handle_client_type(self, client_socket, client_address, message):
        requested_type = message.get("client_type", "")

        if requested_type == "order":
            no = self.client_registry.register_order(client_socket, client_address)
            self.broadcaster.send_menu(client_socket, self.menu_model)
            # server 디버깅용 print
            print(f"[system] {no}번째 order 접속")
            return "order", False

        elif requested_type == "kitchen":
            no = self.client_registry.register_kitchen(client_socket, client_address)
            # server 디버깅용 print
            print(f"[system] {no}번째 kitchen 접속")
            return "kitchen", False

        elif requested_type == "display":
            no = self.client_registry.register_display(client_socket, client_address)
            # server 디버깅용 print
            print(f"[system] {no}번째 display 접속")
            return "display", False

        # 접속한 클라이언트가 주문, 주방, 전광판이 아닐 경우 소켓 연결 종료
        else:
            print("[system] 미식별 클라이언트 접근, 연결 종료")
            self.protocol.send_message(client_socket, {"type": "auth_result",
                                                         "success": False})
            return None, True

    def _handle_order(self, client_socket, message):
        # 주문 리스트가 공백일때 방어
        if not message.get("items"):
            self.protocol.send_message(client_socket, {"type": "is_success", "success": False})
            return

        '''여러 order 클라이언트가 동시에 주문을 보내도
        번호 발급 -> 방송 -> 응답까지 한 클라이언트씩 순차적으로 처리되도록 lock으로 보호
        (lock 없이 self.order_no += 1만 단독으로 보호해도 번호 중복/누락은 막을 수 있지만,
        방송 순서까지 번호 순서와 어긋날 수 있어 구간 전체를 감싼다)'''
        with self.order_lock:
            now = datetime.datetime.now()
            today = now.date()

            # 자정을 넘겨 날짜가 바뀌었으면 주문번호를 1부터 다시 시작
            if today != self.current_date:
                self.current_date = today
                self.order_no = 0

            # 이제 주문 클라이언트는 items만 송신, 주문 번호는 서버에서 생성
            self.order_no += 1
            current_no = self.order_no
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            current_date = today.strftime("%Y-%m-%d")

            kitchen_message = {"type": "order", "order_no": str(current_no), "items": message.get("items", [])}
            display_message = {"type": "order", "order_no": str(current_no)}
            # 해당 주문 주방에 전달
            self.broadcaster.broadcast_to_kitchen(kitchen_message)
            # 주문 번호만 전광판에 전달
            self.broadcaster.broadcast_to_display(display_message)
            # 주문 클라이언트에 성공 반환
            self.protocol.send_message(client_socket, {"type": "is_success", "order_no": str(current_no), "success": True})
            order_log = {
                "order_date": current_date,
                "order_time": current_time,
                "order_no": str(current_no),
                "items": message.get("items", []),
            }
            self.menu_model.save_ordered_menu(order_log)
            print("주문 접수 완료")

    def _handle_order_complete(self, message):
        order_no = str(message.get("order_no", "")).strip()
        self.broadcaster.broadcast_to_display(message)
        print(f"주문번호 {order_no} 완료 알림 전달")
