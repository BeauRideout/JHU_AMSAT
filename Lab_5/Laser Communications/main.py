import time
import threading

from transmit import transmit
from receive import receive

barrier1 = threading.Barrier(2)
barrier2 = threading.Barrier(2)

time.sleep(3)

TransmitThread = threading.Thread(target=transmit, args=[barrier1, barrier2])
ReceiveThread = threading.Thread(target=receive, args=[barrier1, barrier2])

TransmitThread.start()
ReceiveThread.start()