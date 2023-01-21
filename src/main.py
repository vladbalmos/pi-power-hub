import uasyncio as asyncio
from threadsafe import ThreadSafeQueue
import _thread
import net
# from machine import Pin, Timer
# import net
# import time
# import device


# led = Pin('LED', Pin.OUT)
# _time = Timer()

# def tick(timer):
#     global led
#     global wlan
#     led.toggle()
#     print("Toggling let")
    
# _time.init(freq=2.5, mode=Timer.PERIODIC, callback=tick)

# print(device.features)

# while True:
#     if not net.status():
#         net.connect()
        
#     time.sleep_ms(500)


async def main():
    # setup device and board
    while True:
        print("In here")
        if not net.status():
            net.connect()
        await asyncio.sleep(0)
            

asyncio.run(main())