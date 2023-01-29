.PHONY: run run-no-output monitor upload reset clean ls build
.DEFAULT_GOAL := build

SRC_DIR = src
MAIN = main.py
PORT = /dev/ttyACM0

upload-everything:
	sudo ampy --port $(PORT) put $(SRC_DIR) /

upload-src:
	for f in $(shell ls -p src | grep -v /); do \
		sudo ampy --port $(PORT) put src/$$f; \
	done

reset:
	sudo ampy --port $(PORT) reset --hard

clean:
	for f in $(shell make ls); do \
		sudo ampy --port $(PORT) rm $$f; \
	done
	sudo ampy --port $(PORT) rm lib/primitives
	sudo ampy --port $(PORT) rm lib/threadsafe
	sudo ampy --port $(PORT) rm lib

run: upload-src reset
	sleep 1
	sudo minicom -o -D $(PORT) -b 115200

run-no-output: upload-src
	sudo ampy --port $(PORT) run --no-output $(SRC_DIR)/$(MAIN)
	
monitor:
	sudo minicom -o -D $(PORT) -b 115200
	
ls:
	@sudo ampy --port $(PORT) ls -r

build: upload-everything reset
