import machine
import uasyncio as asyncio
import utime as time
import net

async def main():
    led = machine.Pin('LED', machine.Pin.OUT)
    
    if not net.status():
        net.connect()
    
    
    asyncio.create_task(net.net_loop())
    
    while True:
        led.toggle()
        await asyncio.sleep_ms(500)
        
asyncio.run(main())
asyncio.new_event_loop()