import socket
import threading

# 외부에서 connect시도시 server IPv4 10.10.10.142
HOST = "0.0.0.0"
PORT = 5000


class Server:
    def __init__(self, protocol, menu_model, client_registry, broadcaster, order_router):
        self.host = HOST
        self.port = PORT

        self.protocol = protocol
        self.menu_model = menu_model
        self.client_registry = client_registry
        self.broadcaster = broadcaster
        self.order_router = order_router

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.server_socket:
            self.server_socket.bind((self.host, self.port))

            self.server_socket.listen()
            print("서버 시작, 클라이언트 연결 대기중")
            # accept_input 내부엔 handle_client도 스레딩 중
            server_s = threading.Thread(target=self.accept_input)

            server_s.daemon = True
            server_s.start()

            # 메인 스레드 명령어
            while True:
                comm = input("명령어를 입력해주세요\nex) /list ,order_list ,kitchen_list ,display_list ,order_log\n  --종료 /exit\n")
                if comm == "/list":
                    self.client_registry.client_list()
                elif comm == "/order_list":
                    self.client_registry.order_list()
                elif comm == "/kitchen_list":
                    self.client_registry.kitchen_list()
                elif comm == "/display_list":
                    self.client_registry.display_list()
                elif comm == "/order_log":
                    self.menu_model.show_ordered_menu()
                elif comm == "/exit":
                    print("서버 종료")
                    break

    def accept_input(self):
        while True:
            # 다중 client_socket 접속 accept 생성
            client_socket, client_address = self.server_socket.accept()

            client_accept = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            self.client_registry.add_client(client_socket, client_address)
            # 접속중인 클라이언트 수 확인
            self.client_registry.client_count()
            # client_accept.daemon = True
            client_accept.start()

    # 개별 클라이언트 메시지 송수신 함수
    def handle_client(self, client_socket, client_address):
        '''protocol 사용 각 클라이언트 개별 buffer - 반드시 함수 내부에 선언
        전역 변수로 설정하면 모든 송수신 소켓 객체가 같은 버퍼를 공유해버림'''
        buffer = ""
        # 클라이언트 접속시 접속 클라이언트 제외 전체 알림
        address_text = str(client_address)
        # 소켓 연결될때마다 받은 send_message의 client_type을 확인 후 클라이언트 식별
        client_type = None
        try:
            while True:
                # protocol 사용 json 송수신
                try:
                    # 클라이언트 메시지 수신시 return값으로 받는 buffer, 메시지, 연결 참/거짓
                    buffer, messages, connected = self.protocol.receive_message(client_socket, buffer)
                    # 참/거짓으로 연결 판별
                    if not connected:
                        print(f"{address_text} 클라이언트 연결 끊김")
                        break
                    # 반복루프 탈출용 bool
                    exit_requested = False

                    # sendall() 한번에 여러 딕셔너리 메시지가 와도 반복으로 타입 확인 후 처리
                    for message in messages:
                        print(f"{address_text} : {message}")

                        # 메시지 타입별 실제 처리는 order_router에 위임
                        client_type, exit_requested = self.order_router.handle_message(
                            client_socket, client_address, message, client_type
                        )

                        # for문 내부 "exit"/미식별 클라이언트 -> while까지 탈출
                        if exit_requested:
                            break

                    if exit_requested:
                        break
                except Exception as e:
                    print(f"클라이언트 {client_address}에서 {e} 오류 발생")
                    break
        # 루프 탈출
        finally:
            try:
                client_socket.close()
            except Exception:
                pass
            print(f"{client_type} 연결 종료")
            # 연결 소켓 리스트에서 제거
            self.client_registry.remove_client(client_socket)
            self.client_registry.remove_order_client(client_socket)
            # 접속중인 클라이언트 수 확인
            self.client_registry.client_count()
