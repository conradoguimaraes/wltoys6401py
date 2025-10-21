
import sys
import traceback
import socket
import time

class wltoys6401:
    
    def __init__(self):
        self.car_IP = "172.16.11.1"
        self.handshake_port = 23459
        self.control_port = 23458

        self.tx_frequency_Hz = 20  # 20 Hz

        self.sync_msg_1 = bytes.fromhex("a88a210006000000010000000000")
        self.sync_msg_2 = bytes.fromhex("a88a200008000000010002000000d204")
        self.heartbeat_msg = bytes.fromhex("ca47d500000000006680808000008099")
    #end-def


    def recv_once(self, sock, timeout=0.3):
        sock.settimeout(timeout)
        try:
            data, _ = sock.recvfrom(1024)
            return data
        except Exception:
            return b""
    #end-def

    def handshake(self) -> None:
        #FIXME : not always receiving the ACKs
        hs_rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        hs_rx.bind(("", self.handshake_port))

        hs_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        hs_tx.sendto(self.sync_msg_1, (self.car_IP, self.handshake_port))
        time.sleep(0.003)
        hs_tx.sendto(self.sync_msg_2, (self.car_IP, self.handshake_port))
        
        print("ACK1:", (self.recv_once(hs_rx) or b"").hex())
        print("ACK2:", (self.recv_once(hs_rx) or b"").hex())
        hs_rx.close()
        hs_tx.close()
        return None
    #end-def


    def send_heartbeat(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(self.heartbeat_msg, (self.car_IP, self.control_port))
        s.close()
    #end-def

#end-class


if __name__ == "__main__":
    print("Starting wltoys6401 heartbeat transmitter...")
    car = wltoys6401()
    tx_delay_seconds = 1 / car.tx_frequency_Hz

    while True:
        try:
            car.send_heartbeat()
            print("Heartbeat sent.")
            time.sleep(tx_delay_seconds)
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print(traceback.format_exc())
        #end-try-except
    #end-while
#end-if-else

