class Broadcaster:
    """등록된 클라이언트들에게 protocol을 통해 메시지를 전송한다."""

    def __init__(self, protocol, client_registry):
        self.protocol = protocol
        self.client_registry = client_registry

    # 주방에 주문 번호 전송
    def broadcast_to_kitchen(self, message):
        # 여러 클라이언트에서 동시에 clients 조회, 수정하면 오류 발생 위험 - 리스트[:] = 복사본으로 조회
        for client in self.client_registry.client_kitchen[:]:
            # 주방
            try:
                self.protocol.send_message(client["socket"], message)
            except Exception:
                pass

    def broadcast_to_display(self, message):
        for client in self.client_registry.client_display[:]:
            try:
                # 전광판
                self.protocol.send_message(client["socket"], message)
            except Exception:
                pass

    def send_menu(self, client_socket, menu_model):
        menu = {"type": "menu",
                "content": menu_model.get_menu()}
        self.protocol.send_message(client_socket, menu)
