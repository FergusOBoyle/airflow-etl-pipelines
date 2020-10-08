from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import UrlCsvToS3Operator
from airflow.operators import S3CsvToMssqlOperator
from airflow.operators import S3CsvToPostgresOperator
from airflow.operators.mssql_operator import MsSqlOperator

dag = DAG('traffic_dag', description='Extract traffic data and push to AWS database',
          schedule_interval='5 0 * * *',
          start_date=datetime(2017, 3, 20), catchup=False)

dummy_task = DummyOperator(task_id='dummy_task', dag=dag)



pull_task = UrlCsvToS3Operator( url='https://data.tii.ie/Datasets/TrafficCountData/' + \
                                    '{{(execution_date - macros.timedelta(days=1)).strftime("%Y/%m/%d")}}' + \
                                    '/per-vehicle-records-' + 
                                    '{{(execution_date - macros.timedelta(days=1)).strftime("%Y-%m-%d")}}' + \
                                    '.csv',
                                bucket='traffic-reports',
                                s3_filename='traffic-per-vehicle/' + \
                                    '{{ (execution_date - macros.timedelta(days=1)).strftime("%Y/%m/%d")}}'  + \
                                    '/traffic-report.csv',
                                task_id='url_task_id', dag=dag)  


 postgres_write_task = S3CsvToPostgresOperator(  bucket='traffic-reports',
                                                 s3_filename='traffic-report-' + \
                                                     '{{ (execution_date - macros.timedelta(days=1)).strftime("%Y-%m-%d")}}' + \
                                                     '.csv', 
                                                 postgres_conn_id='postgres_aws',
                                                 task_id='s3_to_postgres_task_id',
                                                 dag=dag)


dummy_task >> pull_task >> postgres_write_task
