import utime
import machine
import uasyncio as asyncio
from lib.primitives.queue import Queue
from lib.threadsafe.threadsafe_queue import ThreadSafeQueue
import device
import net

def valid_state_update_request(msg):
    if 'request' not in msg:
        return False
        
    if msg['request'] != 'state-update':
        return False

    if 'payload' not in msg:
        return False
        
    payload = msg['payload']
    
    if 'deviceId' not in payload or 'featureId' not in payload:
        return False
        
    if payload['deviceId'] != device.id:
        return False
        
    return device.has_feature(payload['featureId'])
        
async def main():
    led = machine.Pin('LED', machine.Pin.OUT)

    device_registration = device.init_state()
    msg_queue = Queue(32)
    
    print("Initializing connection")
    asyncio.create_task(net.init(device_registration, msg_queue))
    
    while True:
        led.toggle()
        

        if not msg_queue.empty():
            msg = msg_queue.get_nowait()
            if valid_state_update_request(msg):
                feature_id, new_state = device.update(msg['payload'])
                net.queue_state_publishing(feature_id, new_state)

            
        # if device changed state
            # net.publish(new state)
            
        # if shutdown_on_usb_input
            # poll usb_input
            # if off, turn off
            # net.publish(new state)
        
        await asyncio.sleep_ms(500)
        
asyncio.run(main())
asyncio.new_event_loop()