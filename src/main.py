import machine
import utime as time
import uasyncio as asyncio

async def main():
    led = machine.Pin('LED', machine.Pin.OUT)
    
    while True:
        print("In main loop")
        led.toggle()
        time.sleep_ms(500);
        # Check if wifi connected and connect if not
        
        # Check for received connection messages
        
        # Process messages
            
        # Periodically broadcast device state
        
        # Process interrupts

        # asyncio.sleep_ms(500)
        
asyncio.run(main())