from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import UrlCsvToS3Operator

dag = DAG('my_test_dag', description='Another tutorial DAG',
          schedule_interval='0 12 * * *',
          start_date=datetime(2017, 3, 20), catchup=False)

dummy_task = DummyOperator(task_id='dummy_task', dag=dag)



operator_task = UrlCsvToS3Operator(url='https://data.tii.ie/Datasets/TrafficCountData/' + \
                                    '{{(execution_date - macros.timedelta(days=1)).strftime("%Y/%m/%d")}}' + \
                                    '/per-site-class-aggr-' + 
                                    '{{(execution_date - macros.timedelta(days=1)).strftime("%Y-%m-%d")}}' + \
                                    '.csv',
                                    s3_filename='traffic-report-' + \
                                    '{{ (execution_date - macros.timedelta(days=1)).strftime("%Y-%m-%d")}}' + \
                                    '.csv',
                                    task_id='my_first_operator_task', dag=dag)

dummy_task >> operator_task