import machine
import uasyncio as asyncio
from lib.primitives.queue import Queue
from lib.threadsafe.threadsafe_queue import ThreadSafeQueue
import net
import device

async def main():
    led = machine.Pin('LED', machine.Pin.OUT)

    device.init_state()

    msg_queue = Queue(net.MAX_QUEUE_SIZE)
    
    net.set_registration_info(device.id, device.name, device.features)
    
    if not net.status():
        await net.connect()
        
    asyncio.create_task(net.net_loop(msg_queue))
    # TODO: use the second core for network
    # TODO: set rtc
    # TODO: based on wifi connection status, set the correct led status color
    # update state is sent by the master via udp
    # slave device gets new state via HTTP request from the master and updates itself

    while True:
        led.toggle()
        
        while msg_queue.qsize():
            # If state is received from server, update board and store configuration
            msg = msg_queue.get_nowait()
            print("Received message from server", msg)
            
        # check every second if a cron rule is in effect and update board appropriately
        await asyncio.sleep_ms(500)
        print("main loop iteration")
        
asyncio.run(main())
asyncio.new_event_loop()