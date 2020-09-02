from datetime import timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.mssql_operator import MsSqlOperator

from airflow.utils.dates import days_ago

from extract import extract_traffic_data
#from s3_to_sqlserver import s3_to_sqlserver

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}
dag = DAG(
    'tutorial',
    default_args=default_args,
    description='A simple tutorial DAG',
    schedule_interval=timedelta(days=1),
)

#t1 = PythonOperator(task_id= "extract_traffic", python_callable=extract_traffic_data, dag=dag)

#t1 =  PythonOperator(task_id= "extract_traffic", python_callable=tii_to_s3, dag=dag)

#t2 = PythonOperator(task_id= "extract_traffic", python_callable=s3_to_sqlserver, dag=dag)


"""
t1 = MsSqlOperator(
    task_id='sql-op',
    mssql_conn_id='my_mssql',
    sql='sql/load_traffic.sql',
    dag=dag)
"""

#t2.set_upstream(t1)