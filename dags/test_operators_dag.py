from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import UrlCsvToS3Operator
from airflow.operators import S3CsvToMssqlOperator
from airflow.operators.mssql_operator import MsSqlOperator

dag = DAG('my_test_dag', description='Another tutorial DAG',
          schedule_interval='0 12 * * *',
          start_date=datetime(2017, 3, 20), catchup=False)

dummy_task = DummyOperator(task_id='dummy_task', dag=dag)



pull_task = UrlCsvToS3Operator( url='https://data.tii.ie/Datasets/TrafficCountData/' + \
                                    '{{(execution_date - macros.timedelta(days=1)).strftime("%Y/%m/%d")}}' + \
                                    '/per-site-class-aggr-' + 
                                    '{{(execution_date - macros.timedelta(days=1)).strftime("%Y-%m-%d")}}' + \
                                    '.csv',
                                    bucket='traffic-reports',
                                    s3_filename='traffic-report-' + \
                                    '{{ (execution_date - macros.timedelta(days=1)).strftime("%Y-%m-%d")}}' + \
                                    '.csv',
                                    task_id='my_first_operator_task', dag=dag)                                    

"""
db_write_task = S3CsvToMssqlOperator( task_id='sql_write_task', dag=dag)
"""

db_write_task = MsSqlOperator(
    task_id='sql-op',
    mssql_conn_id='mssql_aws',
    sql='sql/load_traffic.sql',
    dag=dag)


dummy_task >> pull_task >> db_write_task