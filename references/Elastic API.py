from elasticsearch import Elasticsearch
import ssl
import time
from datetime import datetime
import random
context = ssl.create_default_context(cafile="../ca.crt")
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

timestamp = time.time()

client = Elasticsearch(
  "https://192.168.1.168:9200",
  basic_auth=("elastic","password"),
  ssl_context=context
)

'''  
data = {
  'settings': {
  'number_of_shards': 2,
  'number_of_replicas': 0
  },
  'mappings': {
  'properties': {
  'timestamp': {'type': 'date'},
  'location': {'type': 'geo_point'},
  'name': {'type': 'keyword'}
  }
 }
}

client.indices.create(index="test_index", body=data)

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("Index created")
print("---------------------------------")

for i in range(0,100):
  latitude = random.uniform(41.18603966492523, 41.2597959)
  longitude = random.uniform( 1.2206702266907237, 1.987643334236)
  doc_data = {
    'timestamp': datetime.now(),
    'location': {
      "lat": latitude,
      "lon": longitude
    },
    'name': f"MOID{i}"
  }
  client.index(index="test_index", body=doc_data)

client.indices.refresh(index="test_index")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("Data added to the index")
print("---------------------------------")

results = client.search(index="test_index", body={"query": {"match_all": {}}})
print(results)

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("All data read from the index")
print("---------------------------------")

query = {
    "query": {
        "match": {
            "name": "MOID99"
        }
    }
}

client.delete_by_query(index = "test_index", body = query)

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("Document removed by quey")
print("---------------------------------")


query2 = {
    "query": {
        "bool": {
            "must": [
                {"match": {"name": "MOID98"}},
                {"match": {"timestamp":"2024-04-04T14:08:38.627968"}}
            ]
        }
    }
}



doc = client.search(index="test_index", body=query2)
# iterate through all the hits to get the document id

for i in range(len(doc["hits"]["hits"])):
   doc_body = doc["hits"]["hits"][i]["_source"]
   doc_id = doc["hits"]["hits"][i]["_id"]   
   # Once you have the id, make an update request
   doc_body["name"] = "MOID100"
   client.update(index="test_index", id=doc_id, body={"doc": doc_body})
'''

a = client.indices.get_alias(name="[^\\.]*")

print(a)