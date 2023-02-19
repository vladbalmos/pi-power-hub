import board
import uasyncio as asyncio
import ujson as json

_current_rgb_blinking_color = None

id = 'PI_POWER_HUB_001'
name = 'USB Power Hub'
state = None
_state_changes_queue = None

_default_feature = {
    'name': None,
    'id': None,
    'schema': {
        'type': 'boolean',
        'default': 1
    }
}

features = []
_always_on_valid_values = []

for i in range(1, 7):
    f = { key: value  for key, value in _default_feature.items() }
    f['name'] = f'Port {i}'
    f['id'] = f'port_{i - 1}'
    
    _always_on_valid_values.append(f['id'])
    features.append(f)

features.append({
    'name': 'Toggle all ports on/off',
    'description': 'Shortcut for powering on all ports',
    'id': 'toggle_all',
    'schema': {
        'type': 'boolean',
        'default': 1
    }
})

features.append({
    'name': 'Turn off ports when input USB device is OFF',
    'description': '''If a device is connected to the input port and it is powered on,
when the device powers off it will turn off all the ports (excludes ports defined in the "always on" list)
   ''',
    'id': 'power_depends_on_usb_input',
    'schema': {
        'type': 'boolean',
        'default': 1
    }
})
    
features.append({
    'name': 'Always ON ports list',
    'description': 'List all the ports that are always on, regardless of other settings/conditions',
    'id': 'always_on_list',
    'schema': {
        'type': 'list',
        'item': 'string',
        'valid_values': _always_on_valid_values,
        'multiple': True
    }
})
    


def should_turn_off_ports():
    for f in state:
        if f['id'] != 'power_depends_on_usb_input':
            continue
        
        if 'value' in f:
            return f['value']
        else:
            return f['schema']['default']

def init_state(queue):
    global state, _state_changes_queue
    
    _state_changes_queue = queue

    try:
        with open("state.json") as state:
            contents = state.read()
            state = json.loads(contents)
            print("Loading previous state")
    except Exception as e:
        print("No last state found. Initializing using default values")
        print(e)
        state = features.copy()
        
    board.restore_state(state)
    return { 'id': id, 'name': name, 'features': state }

def toggle_port(port_id):
    global state
    # TODO: don't toggle always on ports
    for f in state:
        if f['id'] != port_id:
            continue
        
        if 'value' in f:
            current_value = f['value']
        else:
            current_value = f['schema']['default']
            
        new_value = int(not current_value)
        f['value'] = new_value

        return (port_id, new_value)

    return (None, None)

async def poll_inputs():
    global _state_changes_queue
    while True:
        changes = board.get_changed_inputs()
        await asyncio.sleep_ms(50)
        if not len(changes):
            continue
        
        skip_save_state = False
        state_changes = []
        for (input, value) in changes:
            print(input, value)
            if input != 'usb_in':
                if not value:
                    continue

                feature_id, port_state = toggle_port(input)
                if feature_id:
                    state_changes.append((feature_id, port_state))
            else:
                if not value and should_turn_off_ports():
                    state_changes = toggle_all(0)
                    skip_save_state = True
                    
        if not skip_save_state:
            save_state()

        if len(state_changes):
            for (feature_id, state) in state_changes:
                _state_changes_queue.put_nowait((feature_id, state))
                board.update(feature_id, state)

def has_feature(id):
    for f in features:
        if f['id'] == id:
            return True
    
    return False

def toggle_all(value):
    global state

    # TODO: refactor this
    always_on_ports = list(filter(lambda item: item['id'] == 'always_on_list', state))
    if len(always_on_ports):
        always_on_ports = always_on_ports.pop()
        if 'value' in always_on_ports:
            always_on_ports = always_on_ports['value']
        else:
            always_on_ports = []
    else:
        always_on_ports = []

    changes = [('toggle_all', value)]
    for feature in state:
        if 'port_' in feature['id']:
            if feature['id'] in always_on_ports and not value:
                continue
                
            feature['value'] = value
            board.update(feature['id'], value)
            changes.append((feature['id'], value))

    save_state()
    return changes

def update(data):
    global state
    
    feature_id = data['featureId']
    
    found_feature = None
    for feature in state:
        if feature_id != feature['id']:
            continue
        found_feature = feature
        break
    
    if found_feature is None:
        print(f"Feature not found {feature_id}")
        return [(None, None)]
    
    value = data['state']
    
    return_value = None
    if found_feature['schema']['type'] == 'boolean' or feature_id == 'always_on_list':
        found_feature['value'] = value
        return_value = value

    if feature_id == 'toggle_all':
        print('Turning on all ports')
        return toggle_all(value)

    if return_value is None:
        print("Unsupported feature type")
        return [(None, None)]
    
    
    result = save_state()
    if result:
        print(f'Updated {feature_id} to {return_value}')
        if 'port_' in feature_id:
            board.update(feature_id, return_value)
        return [(feature_id, return_value)]

    return [(None, None)]

def save_state():
    try:
        with open('state.json', 'w') as state_file:
            state_file.write(json.dumps(state))
        return True
    except Exception as e:
        print("Unable to save state")
        print(e)
        return False
    
def led_color(color):
    global _current_rgb_blinking_color
    _current_rgb_blinking_color = color
    board.led_color(color)
    
async def blink_rgb_led():
    global _current_rgb_blinking_color
    timeout_ms = 250
    while True:
        current_color = board.rgb_led_color
        await asyncio.sleep_ms(timeout_ms)
        
        if current_color != 'green':
            board.led_color('off')
            await asyncio.sleep_ms(timeout_ms)
            
            if current_color != _current_rgb_blinking_color:
                current_color = _current_rgb_blinking_color
            board.led_color(current_color)
    
_current_rgb_blinking_color = board.rgb_led
asyncio.create_task(blink_rgb_led())
