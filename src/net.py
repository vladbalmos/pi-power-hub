import uasyncio as asyncio
import wifi_credentials
import ujson as json
from queue import Queue
from lib.mqtt_as import MQTTClient, config

config['ssid'] = wifi_credentials.SSID
config['wifi_pw'] = wifi_credentials.SSID_PASSWORD
config['server'] = '192.168.2.77'
config['queue_len'] = 1

MQTTClient.DEBUG = True

_subscription_topics = {
    'manager': 'vb/devices/request',
    'device': 'vb/devices/power/pihub/request'
}
_publishing_topics = {
    'manager': 'vb/devices/response',
    'device': 'vb/devices/power/pihub/response'
}

_client = None
_publishing_queue = Queue(32)
_connect_task = None
_initial_connection_established = False
_device_registration_info = {}
_main_msg_queue = None

async def register_device():
    global _client
    payload = json.dumps({
        'request': 'registration',
        'requestTopic': _subscription_topics['device'],
        'responseTopic': _publishing_topics['device'],
        'state': _device_registration_info
    })
    print("Registering device", _publishing_topics['manager'], payload)
    await _client.publish(_publishing_topics['manager'], payload, qos = 1)
    print("Registered device")
    
async def process_publishing_queue():
    global _publishing_queue, _client
    
    while True:
        msg = await _publishing_queue.get()
        
        if _client is not None:
            await _client.publish(_publishing_topics['device'], msg, qos = 1)
            print("Published message", msg)
        else:
            await asyncio.sleep_ms(10)
    
def queue_state_publishing(feature_id, new_state):
    global _publishing_queue
    
    if _publishing_queue.full():
        _publishing_queue.make_room()
        
    _publishing_queue.put_nowait(json.dumps({
        'deviceId': _device_registration_info['id'],
        'featureId': feature_id,
        'state': new_state
    }))
    print("Queued new state for publishing")

async def up(client):
    global _initial_connection_established, _client

    while True:
        print("Waiting for connection to be ready")
        await client.up.wait()
        client.up.clear()
        print("Connection (re-)established")
        _client = client

        if not _initial_connection_established:
            _initial_connection_established = True
        
        for k,v in _subscription_topics.items():
            print(f"Subscribing to {v}")
            await client.subscribe(v, 1)

        await register_device()
            
async def messages(client):
    global _main_msg_queue

    async for topic, msg in client.queue:
        if topic == _subscription_topics['manager']:
            await register_device()
            continue

        if topic == _subscription_topics['device']:
            try:
                msg = json.loads(msg)
            except Exception as e:
                print("Failed to parse json message", e)
                await asyncio.sleep_ms(100)
                continue
            
            if _main_msg_queue.full():
                _main_msg_queue.make_room()

            _main_msg_queue.put_nowait(msg)
            await asyncio.sleep_ms(10)
            continue
            
        await asyncio.sleep_ms(100)
        
async def init(device_registration, main_msg_queue):
    global _device_registration_info, \
           _client, \
           _connect_task, \
           _main_msg_queue

    _device_registration_info = device_registration
    _main_msg_queue = main_msg_queue
    
    while not _initial_connection_established:
        client = MQTTClient(config)
        _connect_task = asyncio.create_task(client.connect())
        try:
            print(f"Connecting to {config['server']}")
            await _connect_task
            for couroutine in (up, messages):
                asyncio.create_task(couroutine(client))
            await asyncio.sleep_ms(250)
            print(f"Connection status is: {_initial_connection_established}")
            
            if _initial_connection_established:
                asyncio.create_task(process_publishing_queue())
                
        except BaseException as e:
            print("Connection error", e)
        finally:
            client.close()
            await asyncio.sleep_ms(250)