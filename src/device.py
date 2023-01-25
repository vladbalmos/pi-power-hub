import ujson as json
import board

id = 'PI_POWER_HUB_001'
name = 'USB Power Hub'

state = None

_default_feature = {
    'name': None,
    'id': None,
    'schema': {
        'type': 'boolean',
        'default': 1
    },
    'operations': [
        {
            'action': 'toggle',
        }
    ]
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
    'name': 'Always ON ports list',
    'description': 'List all the ports that are always on, regardless of other settings/conditions',
    'id': 'always_on_list',
    'schema': {
        'type': 'list',
        'item': 'string',
        'valid_values': _always_on_valid_values,
        'multiple': True
    },
    'operations': [
        {
            'action': 'set'
        }
    ]
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
    },
    'operations': [
        {
            'action': 'toggle',
        }
    ]
})

features.append({
    'name': 'Schedule power on/off',
    'id': 'schedule_power_toggle',
    'schema': {
        'type': 'list',
        'item': {
            'id': 'id',
            'port': {
                'type': 'string',
                'valid_values': _always_on_valid_values
            },
            'state': 'boolean',
            'time': 'cron'
        }
    },
    'operations': [
        {
            'action': 'add_item',
        },
        {
            'action': 'delete_item',
        }
    ]
})

def init_state():
    global state

    board.init_gpio()
    try:
        with open("state.json") as state:
            contents = state.read()
            state = json.loads(contents)
    except:
        print("No last state found. Initializing using default values")
        state = features.copy()

    board.restore_state(state)
    
def update(feature_id, config):
    global state

    found_feature = None
    for feature in state:
        if feature_id != feature['id']:
            continue
        found_feature = feature
        break
    
    if found_feature is None:
        print(f"Feature not found {feature_id}")
        return
    
    # if boolean, just set value and update board
    found_feature.value = config.value
    board.update(feature_id)
    
    # if is string, config has operation and value
    
