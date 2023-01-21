.PHONY: run upload reset clean ls build
.DEFAULT_GOAL := build

SRC_DIR = src
MAIN = main.py
PORT = /dev/ttyACM0

upload:
	sudo ampy --port $(PORT) put $(SRC_DIR) /
	
reset:
	sudo ampy --port $(PORT) reset --hard

clean:
	sudo ampy --port $(PORT) rm main.py
	sudo ampy --port $(PORT) rm device.py
	sudo ampy --port $(PORT) rm wifi_credentials.py

run: upload
	sudo ampy --port $(PORT) run $(SRC_DIR)/$(MAIN)
	
ls:
	sudo ampy --port $(PORT) ls -r

build: upload reset
