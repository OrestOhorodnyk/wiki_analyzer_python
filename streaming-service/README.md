
### docker run command 
docker run -d --rm  --name timescaledb -p 5432:5432 -h localhost -e POSTGRES_PASSWORD=wiki -e POSTGRES_DB=wiki timescale/timescaledb:2.0.0-pg12


### Swagger UI ``http://0.0.0.0:8000/docs``


### Terminal websocket client
`https://github.com/vi/websocat`


### 1. Get all Recent Changes as a realtime stream
`ws://0.0.0.0:8000/recent_change`
send ``go`` to start streaming

### 2 Track in real-time the activity of a particular user or a set of users
`ws://0.0.0.0:8000//recent_change_by_users`

send  coma separated user list to start streaming 
eg ``GÜT,Fnielsen,Lettler,Hammersoft,Gamaliel,Lettler,Srich32977,Bdijkstra,Vahurzpu,Bdijkstra,Rar``


### 3 b. Topics to which user has contributed most
eg curl -X GET "http://0.0.0.0:8000/topics_by_user/PhiliPpe%20rogeZ" -H  "accept: application/json"


### 4 Retrieve most active user during the (YEAR|MONTH|DAY)
  ``curl -X GET "http://0.0.0.0:8000/most_active_user/?year=2021&month=2" -H  "accept: application/json"``
