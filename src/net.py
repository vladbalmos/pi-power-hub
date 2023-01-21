import utime
import network
import uselect as select
import usocket as socket
import wifi_credentials

PORT = 3000
POLL_TIMEOUT = 100

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
        utime.sleep_ms(500)
        
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
        self._port = port
        self._addrinfo = socket.getaddrinfo('0.0.0.0', PORT, socket.AF_INET, socket.SOCK_DGRAM)
        self._local_address = self._addrinfo[0][-1]
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(self._local_address)
        self._poller = select.poll()
        self._poller.register(self._socket, select.POLLIN)
        
    def listen(self):
        while True:
            res = self._poller.ipoll(POLL_TIMEOUT, 1)
            
        


   
def _setup_server():
    global _server
    
    if isinstance(_server, Server):
        return
        
    # _server = Server(3000)

def connect(max_retries = 20):
    link_on = _setup_wifi(max_retries)
    if link_on:
        _setup_server()
        
def send(msg):
    print('Sending', msg)