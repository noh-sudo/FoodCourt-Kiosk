class ClientRegistry:
    """접속한 클라이언트(전체/주문/주방/전광판) 목록과 순번 카운터를 관리한다."""

    def __init__(self):
        # 접속 성공한 클라이언트 소켓 담는 list
        self.clients = []

        # 주문, 주방, 전광판 클라이언트 선별
        self.client_order = []
        self.client_kitchen = []
        self.client_display = []

        # n번째 주문, 주방, 알림 클라이언트 구분용
        self.kiosk_no = 0
        self.kitchen_no = 0
        self.display_no = 0

    # accept_input에서 소켓 수락 직후 호출
    def add_client(self, client_socket, client_address):
        self.clients.append({"socket": client_socket,
                              "address": str(client_address)})

    # client_type 등록 - 주문 클라이언트
    def register_order(self, client_socket, client_address):
        self.kiosk_no += 1
        self.client_order.append({"socket": client_socket,
                                   "address": str(client_address),
                                   "client_type": "order",
                                   "kiosk_no": str(self.kiosk_no)})
        return self.kiosk_no

    # client_type 등록 - 주방 클라이언트
    def register_kitchen(self, client_socket, client_address):
        self.kitchen_no += 1
        self.client_kitchen.append({"socket": client_socket,
                                     "address": str(client_address),
                                     "client_type": "kitchen",
                                     "kitchen_no": str(self.kitchen_no)})
        return self.kitchen_no

    # client_type 등록 - 전광판 클라이언트
    def register_display(self, client_socket, client_address):
        self.display_no += 1
        self.client_display.append({"socket": client_socket,
                                     "address": str(client_address),
                                     "client_type": "display",
                                     "display_no": str(self.display_no)})
        return self.display_no

    # 접속종료 클라이언트 리스트에서 제거
    def remove_client(self, client_socket):
        for client in self.clients[:]:
            if client["socket"] == client_socket:
                self.clients.remove(client)
                return client["address"]
        return None

    # 접속 종료한 주문, 주방, 전광판 클라이언트 리스트에서 제거
    # def remove_order_client(self, client_socket):
    #     for client in self.client_order[:]:
    #         if client["socket"] == client_socket:
    #             self.client_order.remove(client)
    #
    #     for client in self.client_kitchen[:]:
    #         if client["socket"] == client_socket:
    #             self.client_kitchen.remove(client)
    #
    #     for client in self.client_display[:]:
    #         if client["socket"] == client_socket:
    #             self.client_display.remove(client)
    #     return None

    # 차이점: client_order/client_kitchen/client_display 3개 리스트에 대해
    # "소켓 일치하면 제거"를 각각 반복하던 for문 3개를, 세 리스트를 순회하는
    # 하나의 for문으로 통합함. 제거 대상 판별/결과는 기존과 동일.
    def remove_order_client(self, client_socket):
        for client_list in (self.client_order, self.client_kitchen, self.client_display):
            for client in client_list[:]:
                if client["socket"] == client_socket:
                    client_list.remove(client)
        return None

    def client_count(self):
        print(f"현재 접속중인 클라이언트 수 : {len(self.clients)}")

    # 메인 스레드 명령어 /list
    # def client_list(self):
    #     print("--접속중인 클라이언트 목록--")
    #     if not self.clients:
    #         print("\n[system] 현재 접속중인 클라이언트가 없습니다.")
    #     for client in self.clients:
    #         # getpeername() = 연결된 소켓 객체의 ip, 포트번호 추출
    #         print(f"- {client['address']}")
    #
    # # /order_list
    # def order_list(self):
    #     print("--주문 클라이언트 주소--")
    #     if not self.client_order:
    #         print("\n[system] 현재 접속중인 클라이언트가 없습니다.")
    #     for client in self.client_order:
    #         print(f"- {client['address']}")
    #
    # # /kitchen_list
    # def kitchen_list(self):
    #     print("--주방 클라이언트 주소--")
    #     if not self.client_kitchen:
    #         print("\n[system] 현재 접속중인 클라이언트가 없습니다.")
    #     for client in self.client_kitchen:
    #         print(f"- {client['address']}")
    #
    # # /display_list
    # def display_list(self):
    #     print("--알림 클라이언트 주소--")
    #     if not self.client_display:
    #         print("\n[system] 현재 접속중인 클라이언트가 없습니다.")
    #     for client in self.client_display:
    #         print(f"- {client['address']}")

    # 차이점: client_list/order_list/kitchen_list/display_list 4개 메서드가
    # "제목 출력 -> 빈 리스트 체크 -> 주소 출력" 동일 패턴을 반복하던 것을
    # 공용 헬퍼 _print_clients(title, clients)로 묶음. 각 메서드는 제목/대상 리스트만
    # 다르게 넘기고, 출력 결과는 기존과 동일함.
    def _print_clients(self, title, clients):
        print(title)
        if not clients:
            print("\n[system] 현재 접속중인 클라이언트가 없습니다.")
        for client in clients:
            print(f"- {client['address']}")

    # 메인 스레드 명령어 /list
    def client_list(self):
        self._print_clients("--접속중인 클라이언트 목록--", self.clients)

    # /order_list
    def order_list(self):
        self._print_clients("--주문 클라이언트 주소--", self.client_order)

    # /kitchen_list
    def kitchen_list(self):
        self._print_clients("--주방 클라이언트 주소--", self.client_kitchen)

    # /display_list
    def display_list(self):
        self._print_clients("--알림 클라이언트 주소--", self.client_display)
