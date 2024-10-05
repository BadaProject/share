# * PLCEmulator class를 생성한다.
#    * 이 class는 init method에서 PLCEmulator의 listen port, PX4의 IP와 listen port를 설정한다.
#    * connect method에서는 UDP socket을 이용하여 PX4 IP와 listen port에 연결한다.
#    * PX4로부터 'hello' 메시지를 수신하면 'hi'를 보낸다.
#    * PX4로부터 'world' 메시지를 수신함녀 'earth'를 보낸다.
# * main method에서는 PLCEmulator class를 생성하고 connect method를 호출한다.

import threading
from time import sleep
from plc import PLCPacket  
import socket


class PLCEmulator:
    def __init__(self, px4_ip='127.0.0.1', plc_listen_port=2005, px4_port=2006):
        self.plc_listen_port = plc_listen_port
        self.px4_ip = px4_ip
        self.px4_port = px4_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.plc_packet = PLCPacket()

    def send(self, data):
        self.sock.send(data, (self.px4_ip, self.px4_port))
    
    def receive_data(self):
        plc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        plc_socket.bind(('', self.plc_listen_port))
        while True:
            data, addr = plc_socket.recvfrom(1024)
            print(data)
            if len(data) > 40:
                print('write request packet')
                if data[20] == self.plc_packet.REQUEST_WRITE:
                    print('OK! write request packet')
            else:
                print('read request packet')
                if data[20] == self.plc_packet.REQUEST_READ:
                    print('OK! read request packet')
                    plc_socket.sendto(self.plc_packet.makeReadRespondPacket(), (self.px4_ip, self.px4_port))
            # if write request packet
            # else read request packet
            print(f"Received data: {data} from {addr} length : {len(data)}")

    def send_write_command(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            while True:
                sock.sendto(self.plc_packet.makeWritePacket(), (self.px4_ip, self.px4_port))
                print('send write command')
                sleep(0.5)

    def send_read_command(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            while True:
                sock.sendto(self.plc_packet.makeReadPacket(), (self.px4_ip, self.px4_port))
                print('send read command')
                sleep(0.5)

    def start(self):
        receive_thread = threading.Thread(target=self.receive_data)
        # send_write_thread = threading.Thread(target=self.send_write_command)    
        # send_read_thread = threading.Thread(target=self.send_read_command)  
        receive_thread.start()
        # send_write_thread.start()
        # send_read_thread.start()

def main():
    emulator = PLCEmulator()
    emulator.start()

if __name__ == "__main__":
    main()