import logging

from airflow.models import BaseOperator
from airflow.plugins_manager import AirflowPlugin
from airflow.utils.decorators import apply_defaults

log = logging.getLogger(__name__)

class S3CsvToMssqlOperator(BaseOperator):

    @apply_defaults
    def __init__(self, *args, **kwargs):
        super(S3CsvToMssqlOperator, self).__init__(*args, **kwargs)

    def execute(self, context):
        log.info("This is the S3 to MsSQL operator")
        

        test = self.xcom_pull(context, key="my_file_name")

        log.info('operator_param: %s', test)

class S3CsvToMssqlPlugin(AirflowPlugin):
    name = "s3_csv_to_mssql_plugin"
    operators = [S3CsvToMssqlOperator]