

import subprocess 
import sys
import yaml

from secrets import get_secret

connection = sys.argv[1]
setting = sys.argv[2]

connections_file = "/usr/local/airflow/connections.yaml"

with open(connections_file) as f:
    config = yaml.safe_load(f)

settings = config['connections'][connection]
secret = eval(get_secret(settings['secrets'], "eu-west-1" ))

if setting == "password":
    print(secret["password"])
elif setting == "username":
    print(secret["username"])
else:
    print(settings[setting])

sys.exit(0)     





