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

    template_fields = ['url', 's3_filename']

    @apply_defaults
    def __init__(self, url: str, s3_filename: str, *args, **kwargs):
        self.url = url
        self.s3_filename = s3_filename
        super(UrlCsvToS3Operator, self).__init__(*args, **kwargs)

    def execute(self, context):
        log.info("Extracting CSV")
        log.info(self.url)


        response = requests.get(self.url)

        bucket = 'traffic-reports'
       
        print(self.s3_filename)
        to_s3(bucket, self.s3_filename, response.content)


class UrlCsvPlugin(AirflowPlugin):
    name = "url_csv_plugin"
    operators = [UrlCsvToS3Operator]