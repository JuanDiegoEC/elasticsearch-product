
from elasticsearch import Elasticsearch

def connect_elasticsearch():
    es = Elasticsearch("http://localhost:9200")
    if es.ping():
        print("Conexion corecta")
    else:
        print("Sin conexion")
    return es
