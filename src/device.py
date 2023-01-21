id = 'PI_POWER_HUB_001'
name = 'USB Power Hub'

_default_feature = {
    'name': None,
    'id': None,
    'schema': {
        'type': 'boolean',
    },
    'operations': [
        {
            'action': 'toggle',
            'default': 1
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
        'item': 'string'
    },
    'operations': [
        {
            'action': 'set',
            'params_schema':  {
                'type': 'list',
                'item': 'string',
                'values': _always_on_valid_values
            }
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
        'type': 'boolean'
    },
    'operations': [
        {
            'action': 'toggle',
            'default': 1
        }
    ]
})

features.append({
    'name': 'Schedule power on/off',
    'id': 'schedule_power_toggle',
    'schema': {
        'type': 'list',
        'item': {
            'port': 'string',
            'state': 'boolean',
            'time': 'cron'
        }
    },
    'operations': [
        {
            'action': 'add_rule',
            'params_schema': {
                'port': {
                    'criteria': 'any',
                    'values': _always_on_valid_values
                },
                'state': {
                    'values': [0, 1]
                },
                'time': {
                    'values': 'cron'
                }
            }
        },
        {
            'action': 'delete_rule',
            'params_schema': 'string'
        }
    ]
})
