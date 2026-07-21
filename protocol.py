import json

# server / client 양쪽 전부 사용할 규율 - 인코딩, 구분자 상수
ENCODING = "utf-8"
DELIMITER = "\n"

# json 송수신 규약
class Protocol:
    def __init__(self):
        self.encoding = ENCODING
        self.delimiter = DELIMITER

    # 메시지를 보낼때
    def send_message(self, sock, message):
        json_text = json.dumps(message, ensure_ascii=False)
        data = (json_text + self.delimiter).encode(self.encoding)

        sock.sendall(data)

    # 메시지를 받은 수신 buffer에서 구분자로 나눠서 받아오는 함수
    def receive_message(self, sock, buffer):
        # 서버-클라이언트 연결 소켓 객체가 수신 buffer에서 받아오는 데이터
        data = sock.recv(1024)

        # 받은 바이트가 없으면 연결 종료
        if not data:
            return buffer, [], False

        # sendall로 받은 바이트를 buffer에 누적 저장
        buffer = buffer + data.decode(self.encoding)
        messages = []

        # 구분자가 누적된 buffer에 있다면 한번에 하나씩 슬라이싱
        while self.delimiter in buffer:
            raw_message, buffer = buffer.split(self.delimiter, 1)

            # 구분자로 나뉜 json 메시지 좌우 공백 제거 후 빈 문자열이 아니라면 딕셔너리로 변환
            if raw_message.strip():
                message = json.loads(raw_message)
                messages.append(message)

        # buffer, 메시지 리스트, 연결 참/거짓 반환
        return buffer, messages, True

