# Time-series service

## Config file
./config.yml
```yaml
mongo_uri: "mongodb://admin:qwerty@localhost:27020"
db_name: "wiki_analyzer"
```

## API methods

### Retrieve a statistic of a particular user
  ``curl -X GET "http://0.0.0.0:8000/most_active_user/?year=2021&month=2" -H  "accept: application/json"``
