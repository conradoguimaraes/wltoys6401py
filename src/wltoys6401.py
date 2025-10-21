
import sys
import traceback
import socket
import time

from utils.hex_functions import hex_to_int, mirror_hex



# --- Normalize a value from [-1, 1] to [min, max] ---
def normalize_to_range(norm_value, min_val, max_val):
    # Clamp to [-1, 1]
    if norm_value < -1:
        norm_value = -1
    elif norm_value > 1:
        norm_value = 1

    # Map [-1, 1] -> [0, 1]
    t = (norm_value + 1) / 2.0
    # Map to [min_val, max_val]
    return int(round(min_val + t * (max_val - min_val)))
#end-def








class wltoys6401:
    
    def __init__(self):
        self.car_IP = "172.16.11.1"
        self.handshake_port = 23459
        self.control_port = 23458

        self.tx_frequency_Hz = 20  # 20 Hz

        self.sync_msg_1 = bytes.fromhex("a88a210006000000010000000000")
        self.sync_msg_2 = bytes.fromhex("a88a200008000000010002000000d204")
        self.heartbeat_msg = bytes.fromhex("ca47d500000000006680808000008099")

        self.max_steering_HEX = "0xFF"
        self.min_steering_HEX = "0x00"

        self.max_throttle_HEX = "0x85"
        self.min_throttle_HEX = mirror_hex(mirror_value = self.max_throttle_HEX)
    #end-def


    # def recv_once(self, sock, timeout=0.3):
    #     #FIXME : not always receiving the ACKs
    #     sock.settimeout(timeout)
    #     try:
    #         data, _ = sock.recvfrom(1024)
    #         return data
    #     except Exception:
    #         return b""
    # #end-def

    # def handshake(self) -> None:
    #     #FIXME : not always receiving the ACKs
    #     hs_rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     hs_rx.bind(("", self.handshake_port))

    #     hs_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     hs_tx.sendto(self.sync_msg_1, (self.car_IP, self.handshake_port))
    #     time.sleep(0.003)
    #     hs_tx.sendto(self.sync_msg_2, (self.car_IP, self.handshake_port))
        
    #     print("ACK1:", (self.recv_once(hs_rx) or b"").hex())
    #     print("ACK2:", (self.recv_once(hs_rx) or b"").hex())
    #     hs_rx.close()
    #     hs_tx.close()
    #     return None
    # #end-def

    def send_message(self, message = None) -> None:
        if message is not None:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(message, (self.car_IP, self.control_port))
            s.close()
        #end-if-else
    #end-def

    def send_heartbeat(self) -> None:
        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # s.sendto(self.heartbeat_msg, (self.car_IP, self.control_port))
        # s.close()
        self.send_message(message = self.heartbeat_msg)
    #end-def
    
    def move(self, throttle_norm = None):
        #input: normalized throttle value in range [-1, 1]
        assert -1.0 <= throttle_norm <= 1.0, "throttle_norm must be in range [-1, 1]"

        results = {}
        if throttle_norm is not None:
            t_min = hex_to_int(self.min_throttle_HEX)
            t_max = hex_to_int(self.max_throttle_HEX)
            throttle_raw = normalize_to_range(throttle_norm, t_min, t_max)
            results["throttle_raw"] = throttle_raw
            results["throttle_hex"] = format(throttle_raw, "02X")
        #end-if-else
    #end-def    

#end-class








if __name__ == "__main__":
    print("Starting wltoys6401 heartbeat transmitter...")
    car = wltoys6401()
    tx_delay_seconds = 1 / car.tx_frequency_Hz

    test_heartbeat = False

    while test_heartbeat:
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

