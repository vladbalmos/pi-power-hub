import device
import machine
import uasyncio as asyncio
from lib.primitives.queue import Queue
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

    msg_queue = Queue(32)
    device_queue = Queue(32)

    device_registration = device.init_state(device_queue)
    
    print("Initializing connection")
    asyncio.create_task(net.init(device_registration, msg_queue))
    asyncio.create_task(device.poll_inputs())
    
    while True:
        led.toggle()
        if not msg_queue.empty():
            msg = msg_queue.get_nowait()
            if valid_state_update_request(msg):
                feature_id, new_state = device.update(msg['payload'])
                net.queue_state_publishing(feature_id, new_state)
            
        while not device_queue.empty():
            led.toggle()
            feature_id, new_state = device_queue.get_nowait()
            net.queue_state_publishing(feature_id, new_state)
            
        await asyncio.sleep_ms(50)
        
asyncio.run(main())
asyncio.new_event_loop()