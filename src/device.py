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
    'name': 'Schedule power on/off',
    'id': 'schedule_power_toggle',
    'schema': {
        'type': 'list',
        'item': {
            'id': {
                'type': 'id'
            },
            'port': {
                'type': 'string',
                'valid_values': _always_on_valid_values
            },
            'time': {
                'type': 'cron'
            },
            'state': {
                'type': 'boolean'
            }
        }
    }
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
    
def update(feature_id, value):
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
    
    if found_feature['schema']['type'] == 'boolean' or feature_id == 'always_on_list':
        found_feature['value'] = value
        return value
    elif feature_id == 'schedule_power_toggle':
        if value['operation'] == 'add':
            if 'value' not in found_feature:
                found_feature['value'] = []
                
            for f in found_feature['value']:
                if f['port'] == value['value']['port'] and f['time'] == value['value']['time'] and f['state'] == value['value']['state']:
                    return 
                
            item = {
                'id': len(found_feature['value']),
                'port': value['value']['port'],
                'time': value['value']['time'],
                'state': value['value']['state']
            }
            
            found_feature['value'].append(item)
            return found_feature['value']
        
    # todo: UPDATE board
