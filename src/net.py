import uasyncio as asyncio
import utime as time
import network
import uselect as select
import usocket as socket
from lib.primitives.queue import Queue, QueueEmpty
import wifi_credentials

PORT = 3000
MAX_QUEUE_SIZE = 32
READ_POLL_TIMEOUT = 20
LOOP_TIMEOUT = 50
UDP_SERVER_PORT = 6000

_udp_read_q = Queue(MAX_QUEUE_SIZE)
_udp_write_q = Queue(MAX_QUEUE_SIZE)
_server = None
_net_status = None
_wlan = None

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
    
def _connect_to_wifi(max_wifi_connect_retries):
    global _wlan, _net_status
    
    _wlan.connect(wifi_credentials.SSID, wifi_credentials.SSID_PASSWORD)
    
    max_retries = max_wifi_connect_retries

    is_connected = False
    while max_retries > 0:
        status = _wlan.status()

        if status == network.STAT_GOT_IP:
            is_connected = True
            break

        max_retries -= 1
        time.sleep_ms(500)
        
    if is_connected:
        _net_status = _wlan.ifconfig()
        
    return is_connected
    

def _setup_wifi(max_retries):
    global _wlan

    if status():
        return True
        
    if _wlan is None:
        _wlan = network.WLAN(network.STA_IF)
        
    if not _wlan.active():
        _wlan.active(True)
        
    return _connect_to_wifi(max_retries)


class Server:

    def __init__(self, port):
        global _net_status
        self._port = port
        self._addrinfo = socket.getaddrinfo('0.0.0.0', PORT, socket.AF_INET, socket.SOCK_DGRAM)
        self._local_address = self._addrinfo[0][-1]
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(self._local_address)
        self._read_poller = select.poll()
        self._read_poller.register(self._socket, select.POLLIN)
        
        self._broadcast_address = socket.getaddrinfo('255.255.255.255', UDP_SERVER_PORT, socket.AF_INET, socket.SOCK_DGRAM)[0][-1]

        
    async def start(self):
        global _udp_write_q, _udp_read_q
        while True:
            result = self._read_poller.poll(READ_POLL_TIMEOUT)
            if len(result):
                start = time.ticks_ms()
                for _ in result:
                    data = self._socket.recv(1024)
                    await _udp_read_q.put(data)
                duration = time.ticks_ms() - start
                
                if duration < READ_POLL_TIMEOUT:
                    await asyncio.sleep_ms(READ_POLL_TIMEOUT - duration)
                    
            while _udp_write_q.qsize():
                to_send = _udp_write_q.get_nowait()
                self.send(to_send)
                
            await asyncio.sleep_ms(LOOP_TIMEOUT)
            
    def send(self, msg):
        if not status():
            connect()
            
        max_send_retries = 5
        while max_send_retries > 0:
            try:
                self._socket.sendto(msg, self._broadcast_address)
                break
            except Exception as e:
                max_send_retries -= 1
                print(e)
                connect()
   
def _setup_server():
    global _server
    
    if isinstance(_server, Server):
        return
        
    _server = Server(3000)

def connect(max_retries = 20):
    link_on = _setup_wifi(max_retries)
    if link_on:
        _setup_server()
        
def register(server_location):
    print('Registering with server', server_location)
        
async def net_loop():
    global _udp_write_q, _udp_read_q, _server
    
    asyncio.create_task(_server.start())
    
    while True:
        await _udp_write_q.put("question:whereareyou")
        
        while _udp_read_q.qsize():
            reply = _udp_read_q.get_nowait()
            register(reply)

        await asyncio.sleep(1);

        