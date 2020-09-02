import logging

from airflow.models import BaseOperator
from airflow.plugins_manager import AirflowPlugin
from airflow.utils.decorators import apply_defaults

import boto3
import os
import time
from datetime import datetime, timedelta
from sys import platform

import csv
import codecs
import requests
import yaml

def to_s3(bucket,filename, content):
        client = boto3.client('s3')
        key = filename
        client.put_object(Bucket=bucket, Key=key, Body=content)

log = logging.getLogger(__name__)

class UrlCsvToS3Operator(BaseOperator):
    """
    Airflow operator that lets user provide a csv url and a filename
    in S3 and the file will be transferred.

    The url and the s3_filename fields are templated.   
    """

    template_fields = ['url', 's3_filename']

    @apply_defaults
    def __init__(self, url: str, bucket: str, s3_filename: str, *args, **kwargs):
        """
        Args:
            url: url of the CSV to be downloaded
            s3_filename: Filename to use in S3.
        """

        self.url = url
        self.bucket = bucket
        self.s3_filename = s3_filename
        super(UrlCsvToS3Operator, self).__init__(*args, **kwargs)

    def execute(self, context):
        log.info("Extracting CSV")
        log.info(self.url)

        response = requests.get(self.url)
       
        print(self.s3_filename)
        to_s3(self.bucket, self.s3_filename, response.content)

        self.xcom_push(context, "my_file_name", "Fergs")

        #self.s3_filename.xcom_push

class UrlCsvPlugin(AirflowPlugin):
    name = "url_csv_plugin"
    operators = [UrlCsvToS3Operator]