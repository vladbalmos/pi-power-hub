# System requirements
* micropython
* ampy (pip3 install adafruit-ampy)
* minicom (optional)


# Development
Build micropython:

    cd [mycropython-dir]
    make -C mpy-cross

    cd [mycropython-dir]/ports/rp2
    make BOARD=PICO_W submodules
    make BOARD=PICO_W clean
    make BOARD=PICO_W
    
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
    