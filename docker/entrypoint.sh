#!/usr/bin/env bash

# User-provided configuration must always be respected.
#
# Therefore, this script must only derives Airflow AIRFLOW__ variables from other variables
# when the user did not provide their own configuration.

TRY_LOOP="20"

# Global defaults and back-compat
: "${AIRFLOW_HOME:="/usr/local/airflow"}"
: "${AIRFLOW__CORE__FERNET_KEY:=${FERNET_KEY:=$(python -c "from cryptography.fernet import Fernet; FERNET_KEY = Fernet.generate_key().decode(); print(FERNET_KEY)")}}"
: "${AIRFLOW__CORE__EXECUTOR:=${EXECUTOR:-Sequential}Executor}"

# Load DAGs examples (default: Yes)
if [[ -z "$AIRFLOW__CORE__LOAD_EXAMPLES" && "${LOAD_EX:=n}" == n ]]; then
  AIRFLOW__CORE__LOAD_EXAMPLES=False
fi

export \
  AIRFLOW_HOME \
  AIRFLOW__CORE__EXECUTOR \
  AIRFLOW__CORE__FERNET_KEY \
  AIRFLOW__CORE__LOAD_EXAMPLES \
  

# Install custom python package if requirements.txt is present
if [ -e "/requirements.txt" ]; then
    $(command -v pip) install --user -r /requirements.txt
fi

#Set up coonection with the backend database.
#Connection parameters are specified in the connections.yaml config file
POSTGRES_HOST=$(python "$AIRFLOW_HOME"/scripts/get_conn_setting.py backend_database conn_host)
POSTGRES_PORT=$(python "$AIRFLOW_HOME"/scripts/get_conn_setting.py backend_database conn_port)
POSTGRES_USER=$(python "$AIRFLOW_HOME"/scripts/get_conn_setting.py backend_database username)
POSTGRES_PASSWORD=$(python "$AIRFLOW_HOME"/scripts/get_conn_setting.py backend_database password)
POSTGRES_DB=$(python "$AIRFLOW_HOME"/scripts/get_conn_setting.py backend_database conn_schema)
POSTGRES_EXTRAS=""

echo "$POSTGRES_PASSWORD"
echo "$POSTGRES_PORT"
echo "$POSTGRES_HOST"

AIRFLOW__CORE__SQL_ALCHEMY_CONN="postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}${POSTGRES_EXTRAS}"
export AIRFLOW__CORE__SQL_ALCHEMY_CONN


wait_for_port "Postgres" "$POSTGRES_HOST" "$POSTGRES_PORT"


# CeleryExecutor drives the need for a Celery broker, here Redis is used
if [ "$AIRFLOW__CORE__EXECUTOR" = "CeleryExecutor" ]; then
  # Check if the user has provided explicit Airflow configuration concerning the broker
  if [ -z "$AIRFLOW__CELERY__BROKER_URL" ]; then
    # Default values corresponding to the default compose files
    : "${REDIS_PROTO:="redis://"}"
    : "${REDIS_HOST:="redis"}"
    : "${REDIS_PORT:="6379"}"
    : "${REDIS_PASSWORD:=""}"
    : "${REDIS_DBNUM:="1"}"

    # When Redis is secured by basic auth, it does not handle the username part of basic auth, only a token
    if [ -n "$REDIS_PASSWORD" ]; then
      REDIS_PREFIX=":${REDIS_PASSWORD}@"
    else
      REDIS_PREFIX=
    fi

    AIRFLOW__CELERY__BROKER_URL="${REDIS_PROTO}${REDIS_PREFIX}${REDIS_HOST}:${REDIS_PORT}/${REDIS_DBNUM}"
    export AIRFLOW__CELERY__BROKER_URL
  else
    # Derive useful variables from the AIRFLOW__ variables provided explicitly by the user
    REDIS_ENDPOINT=$(echo -n "$AIRFLOW__CELERY__BROKER_URL" | cut -d '/' -f3 | sed -e 's,.*@,,')
    REDIS_HOST=$(echo -n "$POSTGRES_ENDPOINT" | cut -d ':' -f1)
    REDIS_PORT=$(echo -n "$POSTGRES_ENDPOINT" | cut -d ':' -f2)
  fi

  wait_for_port "Redis" "$REDIS_HOST" "$REDIS_PORT"
fi

case "$1" in
  webserver)
    airflow initdb
    python "$AIRFLOW_HOME"/scripts/config_conns.py
    if [ "$AIRFLOW__CORE__EXECUTOR" = "LocalExecutor" ] || [ "$AIRFLOW__CORE__EXECUTOR" = "SequentialExecutor" ]; then
      # With the "Local" and "Sequential" executors it should all run in one container.
      airflow scheduler &
    fi
    exec airflow webserver
    ;;
  worker|scheduler)
    # Give the webserver time to run initdb.
    sleep 10
    exec airflow "$@"
    ;;
  flower)
    sleep 10
    exec airflow "$@"
    ;;
  version)
    exec airflow "$@"
    ;;
  *)
    # The command is something like bash, not an airflow subcommand. Just run it in the right environment.
    exec "$@"
    ;;
esac

