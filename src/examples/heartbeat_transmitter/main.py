import sys
import traceback
import time

from wltoys6401 import wltoys6401


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