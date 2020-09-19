#!/usr/bin/env bash



: "${AIRFLOW_HOME:="/usr/local/airflow"}"

export AIRFLOW_HOME

python "$AIRFLOW_HOME"/scripts/config_conns.py