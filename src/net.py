import uasyncio as asyncio
import wifi_credentials

_device_registration_info = {}

async def init(device_registration, main_msg_queue):
    # start timer to check if connected, cancel connect task if more than X seconds passed
    # if initial connection failed, retry until connected
    pass
        
def set_registration_info(did, dname, dfeatures):
    global _device_registration_info
    _device_registration_info = {
        'id': did,
        'name': dname,
        'features': dfeatures
    }