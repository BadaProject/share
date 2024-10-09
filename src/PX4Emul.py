# * PX4Emulator class를 생성한다.
#    * 이 class는 init method에서 PX4Emulator의 listen port, PLC의 IP와 listen port를 설정한다.
#    * connect method에서는 UDP socket을 이용하여 PLC IP와 listen port에 연결한다.
#    * 0.2초마다 write_command method를 호출한다. 
#    * 0.2초마다 read_command method를 호출한다.
#    * write_command method에서는 PLC에게 'hello'를 보낸다.
#    * read_command method에서는 PLC에게 'world' 를 보낸다.
#    * PX4Emulator의 listen port에서 PLC로부터 수신한 데이터를 출력한다.
# * main method에서는 PX4Emulator class를 생성하고 connect method를 호출한다.
import threading
from time import sleep
from plc import PLCPacket, PlcToPx4Packet
import socket

class PX4Emulator:
    def __init__(self, plc_ip='127.0.0.1', plc_port=2005, px4_listen_port=2006):
        self.px4_listen_port = px4_listen_port
        self.plc_ip = plc_ip
        self.plc_port = plc_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.plc_packet = PLCPacket()
        self.px4_ip = '192.168.2.200'
        self.sock.bind(('', self.px4_listen_port))
        self.isWriteCommand = False
    def send(self, data):
        self.sock.send(data, (self.plc_ip, self.plc_port))
    
    def receive_data(self):
        # px4_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # px4_socket.bind((self.px4_ip, self.px4_listen_port))
        while True:
            data, addr = self.sock.recvfrom(1024)
            if data[20] == self.plc_packet.RESPONSE_READ:
                if data[19] == self.plc_packet.getCheckSum(data, 0, 19):
                    print('-----PLC RESPONSE_READ Received!!! -------------')
                    plc_packet = PlcToPx4Packet()
                    plc_packet.parseDataBytes(data[32:])
                    plc_packet.printData()
                    # 32번째 index부터 30bytes 데이터를 short int 15개에 담는다.
            print(data)
            print(f"Received data: {data} from {addr} length : {len(data)}")

    def send_data(self):
        
            while True:
                if self.isWriteCommand:
                    self.sock.sendto(self.plc_packet.makeWritePacket(), (self.plc_ip, self.plc_port))
                    print('send write command')
                else:
                    self.sock.sendto(self.plc_packet.makeReadPacket(), (self.plc_ip, self.plc_port))
                    print('send read command')
                sleep(0.5)
                self.isWriteCommand = not self.isWriteCommand
    def send_write_command(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            while True:
                sock.sendto(self.plc_packet.makeWritePacket(), (self.plc_ip, self.plc_port))
                print('send write command')
                sleep(0.5)

    def send_read_command(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            while True:
                sock.sendto(self.plc_packet.makeReadPacket(), (self.plc_ip, self.plc_port))
                print('send read command')
                sleep(0.5)

    def start(self):
        receive_thread = threading.Thread(target=self.receive_data)
        send_thread = threading.Thread(target=self.send_data)
        receive_thread.start()
        send_thread.start()
        
def main():
    emulator = PX4Emulator()
    emulator.start()
 
if __name__ == "__main__":
    main()