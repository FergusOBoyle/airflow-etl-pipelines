import logging

from airflow.models import BaseOperator
from airflow.plugins_manager import AirflowPlugin
from airflow.utils.decorators import apply_defaults

log = logging.getLogger(__name__)

class S3CsvToMssqlOperator(BaseOperator):

    @apply_defaults
    def __init__(self, my_operator_param, *args, **kwargs):
        self.operator_param = my_operator_param
        super(S3CsvToMssqlOperator, self).__init__(*args, **kwargs)

    def execute(self, context):
        log.info("This is the S3 to MsSQL operator")
        log.info('operator_param: %s', self.operator_param)

class S3CsvToMssqlPlugin(AirflowPlugin):
    name = "s3_csv_to_mssql_plugin"
    operators = [S3CsvToMssqlOperator]