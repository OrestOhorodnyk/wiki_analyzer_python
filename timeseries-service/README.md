# Time-series service

## Config file
./config.yml
```yaml
mongo_uri: "mongodb://admin:qwerty@localhost:27020"
db_name: "wiki_analyzer"
```

## API methods

### Retrieve a statistic of a particular user
  ``curl -X GET "http://0.0.0.0:8000//chart/contribution/{username}?limit=100" -H  "accept: application/json"``

#### Params

`[int]limit` default 100

`[str]granularity` default `year`

available:
* `year`
* `month`
* `day`
* `hour`

#### Response
```json
{
    "data": [
        {
            "x": "2021-01-19T09:00:00",
            "y": 543
        },
        {
            "x": "2021-01-19T10:00:00",
            "y": 2074
        }
    ]
}
```