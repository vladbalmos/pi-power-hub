# System requirements
* micropython
* ampy (pip3 install adafruit-ampy)
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
    
    
# TODO
* add reset btn to clear device state
* add btn for each port to manual toggle power

# Topics
* vb/devices/power/pihub/request
    - device subscribes for state change requests
* vb/devices/power/pihub/response
    - device publishes state changes
* vb/devices/request
    - device subscribes for registration requests
* vb/devices/response
    - device publishes device registration data
