import machine
import uasyncio as asyncio
from lib.primitives.queue import Queue
from lib.threadsafe.threadsafe_queue import ThreadSafeQueue
import net
import device

async def main():
    led = machine.Pin('LED', machine.Pin.OUT)

    device_registration = device.init_state()
    msg_queue = Queue(32)
    
    await net.init(device_registration, msg_queue)
    
    while True:
        led.toggle()
        
        # get msg from queue
            # process msg
            
        # if device changed state
            # net.publish(new state)
            
        # if shutdown_on_usb_input
            # poll usb_input
            # if off, turn off
            # net.publish(new state)
        
        await asyncio.sleep_ms(500)
        
asyncio.run(main())
asyncio.new_event_loop()