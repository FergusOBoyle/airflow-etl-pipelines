import logging

from airflow.models import BaseOperator
from airflow.plugins_manager import AirflowPlugin
from airflow.utils.decorators import apply_defaults
from airflow.hooks.mssql_hook import MsSqlHook
import boto3
import csv
import pyodbc
import yaml

log = logging.getLogger(__name__)

connections_file = "/usr/local/airflow/connections.yaml"

def from_s3(bucket,filename):
    client = boto3.client('s3')
    return client.get_object(Bucket=bucket, Key=filename)

def get_secret(secret_name, region_name):

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            
    return secret



class S3CsvToMssqlOperator(BaseOperator):
    """
    Airflow operator that lets user provide csv filename and S3 bucket
    to be transferred to the the traffic aggregation table on SQL server

    The s3_filename field is templated.   
    """

    template_fields = ['s3_filename']

    @apply_defaults
    def __init__(self, bucket: str, s3_filename: str, mssql_conn_id='mssql_default', database=None,   
            *args, **kwargs):
        super(S3CsvToMssqlOperator, self).__init__(*args, **kwargs)
        self.mssql_conn_id = mssql_conn_id
        self.bucket = bucket
        self.s3_filename = s3_filename
        self.database = database

    def execute(self, context):
        log.info("This is the S3 to MsSQL operator")

        log.info("This is the key: %s", self.s3_filename) 
        s3_response = from_s3(bucket=self.bucket, filename=self.s3_filename)
        #s3_response = from_s3(bucket=self.bucket, filename='traffic-report-2017-03-15.csv')
        lines = s3_response['Body'].read().decode('utf-8').splitlines(True)
        reader = csv.reader(lines)

        next(reader)
        params = [[row[0], int(row[1]), int(row[2]), int(row[3]), int(row[4]), int(row[5])] for row in reader]

        #hook = OdbcHook(connection=self.mssql_conn_id)

        
        with open(connections_file) as f:

            config = yaml.safe_load(f)
            settings = config['connections'][self.mssql_conn_id]
            #obtain DB credentials from the AWS secrets manager
            secret = eval(get_secret(settings['secrets'], "eu-west-1" ))
            
            server = settings['conn_host']
            database = settings['conn_schema'] 
            username = secret["username"]
            password = secret["password"]

        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
           
        cursor = cnxn.cursor()
        cursor.fast_executemany = True
    
        sql = "INSERT INTO traffic_daily_aggregates  VALUES (?, ?, ?, ?, ?, ?)"

        cursor.executemany(sql, params)
        cursor.commit()
    

        

class S3CsvToMssqlPlugin(AirflowPlugin):
    name = "s3_csv_to_mssql_plugin"
    operators = [S3CsvToMssqlOperator]

