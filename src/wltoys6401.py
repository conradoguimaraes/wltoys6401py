
import sys
import traceback
import socket
import time

from utils.hex_functions import hex_to_int, mirror_hex
from utils.aux_functions import normalize_to_range






class wltoys6401:
    
    def __init__(self):
        self.car_IP = "172.16.11.1"
        self.handshake_port = 23459
        self.control_port = 23458

        self.tx_frequency_Hz = 20  # 20 Hz

        self.sync_msg_1 = bytes.fromhex("a88a210006000000010000000000")
        self.sync_msg_2 = bytes.fromhex("a88a200008000000010002000000d204")
        
        self.base_msg = bytearray.fromhex("ca47d500000000006680808000008099")
        self.heartbeat_msg = bytearray.fromhex("ca47d500000000006680808000008099")
        self.control_msg = None


        self.max_steering_HEX = "0xFF"
        self.min_steering_HEX = mirror_hex(mirror_value = self.max_steering_HEX)

        self.max_throttle_HEX = "0xA2"
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
    

    def build_control_message(self, value_hex, command = ["throttle", "steering"]):
        assert ("steering" in command) or ("throttle" in command), "command must contain 'steering' or 'throttle'"

        self.control_msg = self.base_msg.copy()
        if ("steering" in command):
            self.control_msg[9] = int(value_hex, 16) & 0xFF
            self.control_msg[14] = self.control_msg[9]  # mirroring byte
        elif ("throttle" in command):
            self.control_msg[10] = int(value_hex, 16) & 0xFF
            self.control_msg[14] = self.control_msg[10]  # mirroring byte
        #end-if-else

        # print("Control message:", self.control_msg.hex())
        return self.control_msg
    #return

    def move(self, throttle_norm = None, steering_norm = None) -> None:
        #input: normalized throttle value in range [-1, 1]
        if throttle_norm is None and steering_norm is None: raise ValueError("At least one of throttle_norm or steering_norm must be provided.")
        if steering_norm is not None: assert -1.0 <= steering_norm <= 1.0, "steering_norm must be in range [-1, 1]"
        if throttle_norm is not None: assert -1.0 <= throttle_norm <= 1.0, "throttle_norm must be in range [-1, 1]"

        results_throttle = {}
        if throttle_norm is not None:
            t_min = hex_to_int(self.min_throttle_HEX)
            t_max = hex_to_int(self.max_throttle_HEX)
            throttle_raw = normalize_to_range(throttle_norm, t_min, t_max)
            results_throttle["throttle_raw"] = throttle_raw
            results_throttle["throttle_hex"] = format(throttle_raw, "02X")

            throttle_msg = self.build_control_message(value_hex = results_throttle["throttle_hex"], command = "throttle")
        #end-if-else

        results_steering = {}
        if steering_norm is not None:
            s_min = hex_to_int(self.min_steering_HEX)
            s_max = hex_to_int(self.max_steering_HEX)
            steering_raw = normalize_to_range(steering_norm, s_min, s_max)
            results_steering["steering_raw"] = steering_raw
            results_steering["steering_hex"] = format(steering_raw, "02X")

            steering_msg = self.build_control_message(value_hex = results_steering["steering_hex"], command = "steering")
        #end-if-else

        tx_delay_seconds = 1 / car.tx_frequency_Hz
        # if (steering_norm is not None): self.send_message(message = steering_msg)
        if (throttle_norm is not None): self.send_message(message = throttle_msg)
        time.sleep(tx_delay_seconds)
        # if (throttle_norm is not None): self.send_message(message = throttle_msg)
        if (steering_norm is not None): self.send_message(message = steering_msg)

        return
    #end-def    

#end-class








if __name__ == "__main__":
    test_heartbeat = False
    test_throttle = False
    test_steering = False
    test_throttle_and_steering = True


    print("Starting wltoys6401 heartbeat transmitter...")
    car = wltoys6401()
    tx_delay_seconds = 1 / car.tx_frequency_Hz

    while test_heartbeat:
        print("Sending heartbeat...")
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

    while test_throttle:
        print("Starting throttle test...")

        # Send initial heartbeat before throttle commands
        car.send_heartbeat()
        time.sleep(tx_delay_seconds)

        try:
            # for tn in [-1.0, -0.5, 0.0, 0.5, 1.0]:
            for tn in [-1.0, 0.0, 1.0, 0.4]:
                car.move(throttle_norm = tn)
                print(f"Throttle command sent: {tn}")
                time.sleep(0.2)
            #end-for
            break #exit after one test cycle
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print(traceback.format_exc())
        #end-try-except
    #end-while


    while test_steering:
        print("Starting steering test...")

        # Send initial heartbeat before steering commands
        car.send_heartbeat()
        time.sleep(tx_delay_seconds)

        try:
            # for tn in [-1.0, -0.5, 0.0, 0.5, 1.0]:
            for tn in [-1.0, -0.2, 0.0, 0.2, 1.0]:
                car.move(steering_norm = tn)
                print(f"Steering command sent: {tn}")
                time.sleep(1)
            #end-for
            car.move(steering_norm = 0.0)
            break #exit after one test cycle
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print(traceback.format_exc())
        #end-try-except
    #end-while



    while test_throttle_and_steering:
        #FIXME Still not smooth enough
        print("Starting throttle and steering test...")

        # Send initial heartbeat before throttle and steering commands
        car.send_heartbeat()
        time.sleep(tx_delay_seconds)

        try:
            # test_commands = [(-1.0, -1.0), (0.0, 0.0), (1.0, 1.0), (0.5, -0.5), (-0.5, 0.5)]
            test_commands = [(1.0, -1.0), (1.0, -1.0), (1.0, -1.0)]
            for tn, sn in test_commands:
                car.move(throttle_norm = tn, steering_norm = sn)
                print(f"Throttle and Steering command sent: {tn}, {sn}")
                # time.sleep(tx_delay_seconds)
            #end-for
            car.move(throttle_norm = 0.0, steering_norm = 0.0)
            break #exit after one test cycle
        except KeyboardInterrupt:
            car.move(throttle_norm = 0.0, steering_norm = 0.0)
            sys.exit(0)
        except:
            print(traceback.format_exc())
        #end-try-except

#end-if-else