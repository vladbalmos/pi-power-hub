import uasyncio as asyncio
import utime as time
import network
import uselect as select
import usocket as socket
import urequests as requests
from lib.primitives.queue import Queue
import wifi_credentials

PORT = 3000
MAX_QUEUE_SIZE = 128
NET_LOOP_TIMEOUT = 500
READ_POLL_TIMEOUT = 1
LOOP_TIMEOUT = 1
UDP_SERVER_PORT = 6000

_wlan = None

_main_msg_queue = None
_udp_read_q = Queue(MAX_QUEUE_SIZE)
_udp_write_q = Queue(MAX_QUEUE_SIZE)
_udp_server = None
_net_status = None
_device_registration_info = {}
_http_server_address = None

_processed_messages = []

def status_str(status):
    if status == network.STAT_CONNECT_FAIL:
        return 'unknown_err'
        
    if status == network.STAT_CONNECTING:
        return 'connecting'
        
    if status == network.STAT_NO_AP_FOUND:
        return 'access_point_reply_err'
        
    if status == network.STAT_IDLE:
        return 'idle'
        
    if status == network.STAT_WRONG_PASSWORD:
        return 'auth_err'
        
    if status == network.STAT_GOT_IP:
        return 'ok'

def status():
    global _wlan
    if _wlan is None:
        return False
        
    if not _wlan.active():
        return False
        
    return _wlan.isconnected()
    
async def _connect_to_wifi(max_wifi_connect_retries):
    global _wlan, _net_status
    
    print("Connecting to network...")
    _wlan.connect(wifi_credentials.SSID, wifi_credentials.SSID_PASSWORD)
    
    max_retries = max_wifi_connect_retries

    is_connected = False
    while max_retries > 0:
        status = _wlan.status()
        print(f'WIFI status is {status_str(status)}')

        if status == network.STAT_GOT_IP:
            is_connected = True
            break

        max_retries -= 1
        await asyncio.sleep_ms(500)
        
    if is_connected:
        print("WIFI connected")
        _net_status = _wlan.ifconfig()
        print('ifconfig: ', _net_status)
    else:
        print("Unable to connect to WIFI")
        
    return is_connected
    

async def _setup_wifi(max_retries):
    global _wlan

    if status():
        return True
        
    if _wlan is None:
        _wlan = network.WLAN(network.STA_IF)
        print("Created interface")
        
    if not _wlan.active():
        _wlan.active(True)
        print("Activated interface")
        
    return await _connect_to_wifi(max_retries)

class Server:

    def __init__(self, port):
        global _net_status
        self._port = port
        self._addrinfo = socket.getaddrinfo('0.0.0.0', PORT, socket.AF_INET, socket.SOCK_DGRAM)
        self._local_address = self._addrinfo[0][-1]
        self._read_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._read_socket.setblocking(False)
        self._read_socket.bind(self._local_address)
        self._read_poller = select.poll()
        self._read_poller.register(self._read_socket, select.POLLIN)

        self._write_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._write_socket.setblocking(False)
        self._broadcast_address = socket.getaddrinfo('255.255.255.255', UDP_SERVER_PORT, socket.AF_INET, socket.SOCK_DGRAM)[0][-1]

        
    async def read_loop(self):
        global _udp_read_q
        while True:
            result = self._read_poller.poll(READ_POLL_TIMEOUT)
            if len(result):
                for _ in result:
                    data = self._read_socket.recv(128)
                    await _udp_read_q.put(data)
                
            await asyncio.sleep_ms(LOOP_TIMEOUT)

    async def write_loop(self):
        global _udp_write_q
        while True:
            while _udp_write_q.qsize():
                to_send = _udp_write_q.get_nowait()
                await self.send(to_send)
                
            await asyncio.sleep_ms(LOOP_TIMEOUT)
            
    async def send(self, msg):
        if not status():
            await connect()
            
        max_send_retries = 5
        while max_send_retries > 0:
            try:
                self._write_socket.sendto(msg, self._broadcast_address)
                break
            except Exception as e:
                max_send_retries -= 1
                print(e)
                await connect()
   
def _setup_server():
    global _udp_server
    
    if isinstance(_udp_server, Server):
        return
        
    _udp_server = Server(3000)

async def connect(max_retries = 20):
    link_on = await _setup_wifi(max_retries)
    if link_on:
        _setup_server()
        
def url(_url):
    global _http_server_address
    x = f'{_http_server_address}{_url}'
    return x

def postRequest(url, data = None):
    try:
        response = requests.post(url, json = data, timeout = 1)
        return response.json()
    except Exception as e:
        print("Caught request exception")
        print(e)
        
def getRequest(url):
    try:
        response = requests.get(url, timeout = 1)
        return response.json()
    except Exception as e:
        print("Caught request exception")
        print(e)
        
async def register(_url, port):
    global _http_server_address 
    _http_server_address = 'http://' + ':'.join((_url, port))

    postRequest(url('/device/reg'), _device_registration_info)
        
async def request_state_update(msg_id, feature_id):
    global _processed_messages
    global _main_msg_queue
    if msg_id in _processed_messages:
        return

    _processed_messages.append(msg_id)

    while len(_processed_messages) > 32:
        _processed_messages.pop(0)
        
    _url = f'/device/update?did={_device_registration_info['id']}&fid={feature_id}'
    response = getRequest(url(_url))
    
    if response is None or response['status'] == False:
        return
    
    try:
        payload = {
            "action": "update_feature",
            "feature_id": feature_id,
            "value": response['value']
        }
        
        await _main_msg_queue.put(payload)
    except Exception as e:
        print(response)
        print(e)
        
        
async def process_udp_message(msg):
    msg = msg.decode('ascii')
    msg_segments = msg.split(':')
    prefix = msg_segments[0]
    msg = msg_segments[1:]
    
    
    if prefix == 'hub@':
        return await register(*msg)
    
    if prefix != _device_registration_info['id']:
        return
    
    prefix = msg[0]
    msg = msg[1:]
    
    if prefix == 'request_state_update':
        return await request_state_update(*msg)
    
def set_registration_info(did, dname, dfeatures):
    global _device_registration_info
    _device_registration_info = {
        'id': did,
        'name': dname,
        'features': dfeatures
    }
    
def send_change_confirmation(feature_id, data):
    _url = f'/device/update?did={_device_registration_info['id']}&fid={feature_id}'
    postRequest(url(_url), {"data": data})
    
    
async def net_loop(main_queue):
    global _udp_write_q, _udp_read_q, _udp_server, _main_msg_queue
    
    _main_msg_queue = main_queue

    asyncio.create_task(_udp_server.read_loop())
    asyncio.create_task(_udp_server.write_loop())
    
    last_hub_query = None
    while True:
        if last_hub_query is None or (time.time() - last_hub_query) > 7:
            last_hub_query = time.time()
            await _udp_write_q.put('request:whereareyou')
            continue
        
        while _udp_read_q.qsize():
            msg = _udp_read_q.get_nowait()
            await process_udp_message(msg)

        await asyncio.sleep_ms(NET_LOOP_TIMEOUT);
        