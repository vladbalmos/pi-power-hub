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

def init_state():
    global state

    board.init_gpio()
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

def has_feature(id):
    for f in features:
        if f['id'] == id:
            return True
    
    return False

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
        return (None, None)
    
    value = data['state']
    
    return_value = None
    if found_feature['schema']['type'] == 'boolean' or feature_id == 'always_on_list':
        found_feature['value'] = value
        return_value = value
            
    if return_value is None:
        print("Unsupported feature type")
        return (None, None)
    
    try:
        with open('state.json', 'w') as state_file:
            state_file.write(json.dumps(state))
            
        print(f'Updated {feature_id} to {return_value}')
        return (feature_id, return_value)
    except Exception as e:
        print("Unable to save state")
        print(e)
        
    return (None, None)
    # todo: UPDATE board
