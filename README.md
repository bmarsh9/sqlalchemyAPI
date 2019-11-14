# sqlalchemyAPI

Easily leverage this repo for any application that needs to take data in a database and display front end graphs or expose Restful API endpoints

## Purpose
- Search (fuzzy, regex, etc.), filter, sort, limit, group by, distinct queries in SQLalchemy that is exposed through an API. The data can be stored and searched in indexed columns or columns with JSONB stored
- Can return the data as a JSON, Datatables, ChartJS and/or Python object for either querying or displaying data in graphs

## Testing
- For searching on indexed columns, any complex queries return very quickly
- For JSON columns, I have tested on a table with 500,000 records and queries returned in about a second

## Usage

##### (GET) Can send queries in the URI (note there is a limit of the length)

```
curl -XGET http://localhost/api/raw/backup/testtable?filter=id,eq,5
```

##### (POST) Can send queries in the body for longer and more complex queries and no URI limit

```
import requests,json

#// Set Up Query
#// Any `subkey` array that is empty will mean that the field is not stored with a JSONB type
d = {"query": {
         "or_": [
            {"column":"data","subkeys":["sale"],"op":"gt","value":1732},
            {"column":"data","subkeys":["category"],"op":"eq","value":"win32_computersystemA"},
            {"column":"data","subkeys":["category"],"op":"eq","value":"win32_computersystemB"},
         ],
         "must_":[
            {"column":"data","subkeys":["category"],"op":"eq","value":"win32_computersystemA"},
            {"column":"id","subkeys":[],"op":"eq","value":172}, #// Not searching JSONB field (subkeys empty)
         ],
         "not_": [
            {"column":"data","subkeys":["category"],"op":"ilike","value":"win32_computersystemcoB"},
            {"column":"data","subkeys":["category"],"op":"ilike","value":"win32_computersystem"},
            {"column":"data","subkeys":["sale"],"op":"gt","value":17},
            {"column":"data","subkeys":["category"],"op":"eq","value":"win32_computersystem"},
         ]
     }
}
payload=d

#// Send request to the server
r = requests.get("http://localhost/api/raw/backup/testtable",json=payload)
data=r.json()

#// Print out the data
print json.dumps(data,indent=4)
```

## Next Steps
- Post code of JQuery / JS frontend code that can query the backend API and display graphs
- Include server (Flask) code examples
- Possibly integrate with Elasticsearch for even more advanced querying
- Include documentation on usage
