import subprocess 
import yaml

import boto3
import base64
from botocore.exceptions import ClientError

from secrets import get_secret

connections_file = "/usr/local/airflow/connections.yaml"



print("Setting up connections found in connections configuration file")

with open(connections_file) as f:

    config = yaml.safe_load(f)

    for name,settings in config['connections'].items():
        print("Creating connection: ", name)

         #obtain DB credentials from the AWS secrets manager
        secret = eval(get_secret(settings['secrets'], "eu-west-1" ))

        subprocess.run(['airflow', 'connections', '--add', '--conn_id', settings['conn_id'] ,'--conn_type', settings['conn_type'], '--conn_host', settings['conn_host'], '--conn_port', str(settings['conn_port']), '--conn_schema' , settings['conn_schema'] , '--conn_login', secret["username"] , '--conn_password', secret["password"] ])
