# System requirements
* micropython
* ampy
* minicom (optional)


# Development
Build micropython:

    cd [mycropython-dir]
    make -C mpy-cross

    cd [mycropython-dir]/ports/rp2
    make -j4 BOARD=PICO_W submodules
    make -j4 BOARD=PICO_W clean
    make -j4 BOARD=PICO_W
    
Set wifi SSID & password:

    cp wifi_credentials.template src/wifi_credentials.py
    # edit src/wifi_credentials.py and add SSID & SSID password

Init:

    pip3 install -r requirements.txt
    ./setup.sh
    make build
    
Run:

    make run
    
Clean

    make clean
    
Upload

    make upload
    
Build

    make build
    
    
# Topics
* vb/devices/power/pihub/request
    - device subscribes for state change requests
* vb/devices/power/pihub/response
    - device publishes state changes
* vb/devices/request
    - device subscribes for registration requests
* vb/devices/response
    - device publishes device registration data

# Status LED meanings:
* red
    - board initializing
* blue
    - connecting to mqtt server
* green
    - connected to mqtt server
* yellow
    - lost connection to mqtt