from machine import Pin

PORT_0 = 6
PORT_1 = 8
PORT_2 = 10
PORT_3 = 21
PORT_4 = 19
PORT_5 = 17

INPUT_0 = 7
INPUT_1 = 9
INPUT_2 = 11
INPUT_3 = 20
INPUT_4 = 18
INPUT_5 = 16

USB_IN = 15

output_pins = [PORT_0, PORT_1, PORT_2, PORT_3, PORT_4, PORT_5]
input_pins = [INPUT_0, INPUT_1, INPUT_2, INPUT_3, INPUT_4, INPUT_5, USB_IN]
input_pins_values = []

output_ports = []
input_ports = []

def switch_toggle_handler(change):
    print('Switch detected', change)

for p in output_pins:
    pin = Pin(p, Pin.OUT)
    pin.on()
    output_ports.append(pin)
    
for p in input_pins:
    pin = Pin(p, Pin.IN, Pin.PULL_DOWN)
    input_pins_values.append(pin.value())
    input_ports.append(pin)

def restore_state(state):
    for feature in state:
        if 'port_' in feature['id']:
            if 'value' in feature:
                value = int(feature['value'])
            else:
                value = int(feature['schema']['default'])

            port_index = int(feature['id'][5:])

            # Ports are active low
            output_ports[port_index].value(int(not value))
            
def get_changed_inputs():
    index = 0
    changes = []
    for p in input_ports:
        value = p.value()
        if index == len(input_pins) - 1:
            key = 'ubs_in'
        else:
            key = f'port_{index}'

        if value != input_pins_values[index]:
            changes.append((key, value))
            input_pins_values[index] = value
        index += 1
    return changes

def update(port_id, state):
    index = int(port_id[5:])
    output_ports[index].value(int(not state))