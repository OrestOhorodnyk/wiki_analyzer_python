# wiki_analyzer_python


## Prerequisites
* Docker and docker-compose installed
* ports 8000-8003 are free
* jq installed (not mandatory, just to prettify the curl response)

## Build containers:
* ``cd replicated_log``
* ``docker-compose build``

## Run container
* ``docker-compose up -d``

## Check the status
* ``docker-compose ps``



```
CONTAINER ID   IMAGE                                         COMMAND                   CREATED          STATUS         PORTS                      NAMES
03811ae4c2b5   wiki_analyzer_python_streaming-service        "/bin/bash -c '\n  wh…"   13 minutes ago   Up 7 seconds   127.0.0.1:8001->8000/tcp   wiki_analyzer_python_streaming-service_1
551484deb722   wiki_analyzer_python_user-statistic-service   "/bin/bash -c '\n  wh…"   13 minutes ago   Up 6 seconds   127.0.0.1:8000->8000/tcp   wiki_analyzer_python_user-statistic-service_1
46734ee51526   timescale/timescaledb:2.0.0-pg12              "docker-entrypoint.s…"    13 minutes ago   Up 8 seconds   127.0.0.1:5432->5432/tcp   wiki_analyzer_python_timescaledb_1

```
