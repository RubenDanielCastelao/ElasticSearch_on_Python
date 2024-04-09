import sqlite3 as dbapi
from elasticsearch import Elasticsearch
import ssl
import time
import pandas as pd


context = ssl.create_default_context(cafile="ca.crt")
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

class DBConnection:

    def __init__(self,dbip,user,password, index):
        self.dbip = dbip
        self.user = user
        self.password = password
        self.cliente = None
        self.index_name = index

    def getIndex(self):
        return self.index_name


    def dbConnect (self):

        try:
            if self.cliente is None:
                self.cliente = Elasticsearch(
                    self.dbip,
                    basic_auth=(self.user,self.password),
                    ssl_context=context
                )
                if not self.index_name is None:
                    index_exists = self.cliente.indices.exists(index= self.index_name)
                    doc_count = self.cliente.count(index=self.index_name)['count']
                else:
                    index_exists = False
                    doc_count = 1
                if not index_exists:
                    Exception("Index does not exist")
                if doc_count == 0:
                    raise Exception("Index is empty")

            else:
                print("Conexión de base de datos realizada")
                print(self.index_name)

        except Exception as e:
            print ("Error al conectar a: " + self.dbip + ": " + e)

    def loadIndex(self):
        try:
            if self.index_name is None:
                print("No se ha definido un índice")
                list_of_lists = []
            else:
                response = self.cliente.search(index=self.index_name, body={"query": {"match_all": {}}}, size = 1000)
                results = [hit['_source'] for hit in response['hits']['hits']]
                df = pd.DataFrame(results)
                list_of_lists = df.values.tolist()
                print("Index loaded")
        except Exception as e:
            print("Error loading index: " + str(e))
        else:
            return list_of_lists

    def addQuery(self, data):
        try:
            if self.cliente is None:
                print("Se necesita crear un cliente")
            else:
                doc_data = {
                    'name': data[0],
                    'timestamp': data[1],
                    'location': {
                        "lat": float(data[2]),
                        "lon": float(data[3])
                    },
                    'image': data[4]
                }
                self.cliente.index(index=self.index_name, body=doc_data)

                self.cliente.indices.refresh(index=self.index_name)

        except dbapi.DatabaseError as e:
            print("Erro facendo a inserción: " + str(e))
        else:
            print("Inserción executada")

    def updateQuery(self, data, query):
        try:
            if self.cliente is None:
                print("Se necesita crear un cliente")
            else:
                doc = self.cliente.search(index=self.index_name, body=query)
                # iterate through all the hits to get the document id

                for i in range(len(doc["hits"]["hits"])):
                    doc_body = doc["hits"]["hits"][i]["_source"]
                    doc_id = doc["hits"]["hits"][i]["_id"]
                    # Once you have the id, make an update request
                    doc_body["name"] = data[0]
                    doc_body["timestamp"] = data[1]
                    doc_body["location"] = {"lat": data[2], "lon": data[3]}
                    doc_body["image"] = data[4]
                    self.cliente.update(index=self.index_name, id=doc_id, body={"doc": doc_body})

        except dbapi.DatabaseError as e:
            print("Erro facendo a actualización rexistro: " + str(e))
        else:
            print("Update done")

    def deleteQuery (self, query):
        try:
            if self.cliente is None:
                print("Cliente no creado")
            else:
                response = self.cliente.delete_by_query(index=self.index_name, body=query)
                print(response)

        except Exception as e:
            print("Error realizando el borrado: " + str(e))
        else:
            print("Borrado de registro ejecutado")

    def searchQuery(self, query):
        try:
            if self.index_name is None:
                print("No se ha definido un índice")
                list_of_lists = []
            else:
                print(query)
                response = self.cliente.search(index=self.index_name, body=query)
                results = [hit['_source'] for hit in response['hits']['hits']]
                df = pd.DataFrame(results)
                list_of_lists = df.values.tolist()
                print("Index loaded")
                print(list_of_lists)
        except Exception as e:
            print("Error loading index: " + str(e))
        else:
            return list_of_lists



    def dbClose(self):
        if self.cliente is not None:
            self.cliente.close()
