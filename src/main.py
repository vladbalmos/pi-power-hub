import machine
import uasyncio as asyncio
from lib.primitives.queue import Queue
import net
import device

async def main():
    led = machine.Pin('LED', machine.Pin.OUT)

    device.init_state()

    http_to_server_queue = Queue(net.MAX_QUEUE_SIZE)
    http_from_server_queue = Queue(net.MAX_QUEUE_SIZE)
    
    net.set_registration_info(device.id, device.name, device.features)
    
    if not net.status():
        await net.connect()
        
    asyncio.create_task(net.net_loop(http_to_server_queue, http_from_server_queue))
    # TODO: set rtc
    # TODO: based on wifi connection status, set the correct led status color
    # update state is sent by the master via udp
    # slave device gets new state via HTTP request from the master and updates itself

    while True:
        led.toggle()
        
        while http_from_server_queue.qsize():
            # If state is received from server, update board and store configuration
            msg = http_from_server_queue.get_nowait()
            print("Received message from http server", msg)
            
        # check every second if a cron rule is in effect and update board appropriately
        await asyncio.sleep_ms(500)
        print("main loop iteration")
        
asyncio.run(main())
asyncio.new_event_loop()