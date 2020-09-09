#!/usr/bin/env bash



: "${AIRFLOW_HOME:="/usr/local/airflow"}"


python "$AIRFLOW_HOME"/scripts/config_conns.py