# wiki_analyzer_python
![alt text](https://github.com/OrestOhorodnyk/wiki_analyzer_python/blob/master/diagram.jpg)

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

# Streaming-service


### Terminal websocket client
`https://github.com/vi/websocat`


### 1. Get all Recent Changes as a realtime stream
`ws://0.0.0.0:8001/recent_change`
send ``go`` to start streaming

### 2 Track in real-time the activity of a particular user or a set of users
`ws://0.0.0.0:8001/recent_change_by_users`

send  coma separated user list to start streaming 
eg ``GÜT,Fnielsen,Lettler,Hammersoft,Gamaliel,Lettler,Srich32977,Bdijkstra,Vahurzpu,Bdijkstra,Rar``


# User-statistic-service

### 3 b. Topics to which user has contributed most
eg `curl -X GET "http://0.0.0.0:8000/topics_by_user/PhiliPpe%20rogeZ" -H  "accept: application/json"`
or `curl -X GET "http://0.0.0.0:8000/topics_by_user_rx/PhiliPpe%20rogeZ" -H  "accept: application/json"` The same as previous but implemented on RxPy

### 4 Retrieve most active user during the (YEAR|MONTH|DAY)
  ``curl -X GET "http://0.0.0.0:8000/most_active_user/?year=2021&month=2" -H  "accept: application/json"``

### 5 Retrieve the top 10 topics which have the most number of typo editings
	`curl -X GET "http://localhost:8000/topic_typos_rx" -H  "accept: application/json"`



## To stop and remove containers

``docker-compose stop && docker-compose rm -f``
