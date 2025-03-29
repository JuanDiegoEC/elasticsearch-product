from flask import Flask, request, jsonify
from client import connect_elasticsearch
import json
from sentence_transformers import SentenceTransformer
from flask import render_template


app = Flask(__name__)
es = connect_elasticsearch()
INDEX_NAME = "amazon_products"

# Cargar template Mustache
with open("app/mustache_template.json") as f:
    TEMPLATE = json.load(f)

@app.route("/buscar", methods=["GET"])
def buscar():
    query_string = request.args.get("q", "")

    if not query_string:
        return jsonify({"error": "Falta el parámetro ?q=..."}), 400

    # Reemplazar el template Mustache manualmente
    with open("app/mustache_template.json") as f:
        template = json.load(f)

    # Insertar la query directamente
    template["query"]["multi_match"]["query"] = query_string

    response = es.search(index=INDEX_NAME, body=template)
    resultados = [hit["_source"] for hit in response["hits"]["hits"]]
    return jsonify(resultados)

model = SentenceTransformer('all-MiniLM-L6-v2')

@app.route("/buscar_semantico", methods=["GET"])
def buscar_semantico():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "Falta el parámetro ?q="}), 400

    query_vector = model.encode(query).tolist()

    body = {
        "size": 10,
        "query": {
            "script_score": {
                "query": {
                    "match_all": {}
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {
                        "query_vector": query_vector
                    }
                }
            }
        }
    }

    response = es.search(index=INDEX_NAME, body=body)
    resultados = [
    {k: v for k, v in hit["_source"].items() if k != "embedding"}
    for hit in response["hits"]["hits"]
    ]
    return jsonify(resultados)

@app.route("/similar_products", methods=["GET"])
def similar_products():
    product_name = request.args.get("name", "")
    if not product_name:
        return jsonify({"error": "Falta el parámetro ?name="}), 400

    # Buscar el producto exacto por nombre
    query = {
        "query": {
            "match_phrase": {
                "name": product_name
            }
        }
    }
    res = es.search(index=INDEX_NAME, body=query, size=1)
    if not res["hits"]["hits"]:
        return jsonify({"error": "Producto no encontrado"}), 404

    product = res["hits"]["hits"][0]
    query_vector = product["_source"]["embedding"]

    # Búsqueda semántica por similitud excluyendo el mismo producto
    body = {
        "size": 5,
        "query": {
            "script_score": {
                "query": {
                    "bool": {
                        "must_not": [
                            {"match_phrase": {"name": product_name}}
                        ]
                    }
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {
                        "query_vector": query_vector
                    }
                }
            }
        }
    }

    similar = es.search(index=INDEX_NAME, body=body)
    resultados = [
    {k: v for k, v in hit["_source"].items() if k != "embedding"}
    for hit in similar["hits"]["hits"]
    ]

    return jsonify(resultados)



@app.route("/")
def home():
    query = request.args.get("q", "")
    resultados = []

    if query:
        query_vector = model.encode(query).tolist()
        body = {
            "size": 9,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            }
        }
        res = es.search(index=INDEX_NAME, body=body)
        resultados = [
            {k: v for k, v in hit["_source"].items() if k != "embedding"}
            for hit in res["hits"]["hits"]
        ]

    return render_template("index.html", resultados=resultados, query=query)

if __name__ == "__main__":
    app.run(debug=True)
