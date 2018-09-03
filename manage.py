import json
from configuration import configuration

print('Loaded configuration:')
print(json.dumps(configuration, indent=3, sort_keys=True))
